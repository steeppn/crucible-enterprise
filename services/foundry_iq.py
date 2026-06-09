import os
import json
import logging
import hashlib
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("crucible.services.foundry_iq")

class FoundryIQClient:
    """Azure AI Search client for Foundry IQ knowledge retrieval.
    
    Handles index creation, document upload, and semantic ranking queries
    against the certification knowledge base.
    """

    def __init__(self):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.api_key = os.getenv("AZURE_SEARCH_API_KEY")
        self.index_name = "crucible-knowledge-base"
        self.api_version = "2024-07-01"
        
        if not self.endpoint or not self.api_key:
            logger.warning("AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY not set. Using fallback mode.")
            self._fallback_mode = True
        else:
            self._fallback_mode = False
            self._headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json"
            }

    def _url(self, path: str) -> str:
        base = self.endpoint.rstrip("/")
        return f"{base}/{path}?api-version={self.api_version}"

    def _import_requests(self):
        try:
            import requests
            return requests
        except ImportError:
            raise ImportError("requests package required. Run: pip install requests")

    # ── Index Management ──────────────────────────────────────────────

    def create_index(self) -> dict:
        """Create the knowledge base index with semantic ranking configuration."""
        if self._fallback_mode:
            logger.info("[Fallback] Index creation skipped")
            return {"status": "fallback"}

        requests = self._import_requests()
        
        index_definition = {
            "name": self.index_name,
            "fields": [
                {
                    "name": "id",
                    "type": "Edm.String",
                    "key": True,
                    "filterable": True
                },
                {
                    "name": "cert_id",
                    "type": "Edm.String",
                    "filterable": True,
                    "searchable": True,
                    "facetable": True
                },
                {
                    "name": "title",
                    "type": "Edm.String",
                    "searchable": True,
                    "retrievable": True
                },
                {
                    "name": "content",
                    "type": "Edm.String",
                    "searchable": True,
                    "retrievable": True
                },
                {
                    "name": "section",
                    "type": "Edm.String",
                    "filterable": True,
                    "searchable": True,
                    "facetable": True
                },
                {
                    "name": "skill_domain",
                    "type": "Edm.String",
                    "filterable": True,
                    "searchable": True,
                    "facetable": True
                },
                {
                    "name": "source_file",
                    "type": "Edm.String",
                    "filterable": True
                }
            ],
            "semantic": {
                "configurations": [
                    {
                        "name": "crucible-semantic-config",
                        "prioritizedFields": {
                            "titleField": {"fieldName": "title"},
                            "prioritizedContentFields": [
                                {"fieldName": "content"},
                                {"fieldName": "section"}
                            ],
                            "prioritizedKeywordsFields": [
                                {"fieldName": "skill_domain"},
                                {"fieldName": "cert_id"}
                            ]
                        }
                    }
                ]
            }
        }

        response = requests.put(
            self._url(f"indexes('{self.index_name}')"),
            headers=self._headers,
            json=index_definition
        )
        response.raise_for_status()
        logger.info(f"Index '{self.index_name}' created successfully")
        return response.json()

    def index_exists(self) -> bool:
        """Check if the index already exists."""
        if self._fallback_mode:
            return False

        requests = self._import_requests()
        response = requests.get(
            self._url("indexes"),
            headers=self._headers
        )
        response.raise_for_status()
        indexes = response.json().get("value", [])
        return any(idx["name"] == self.index_name for idx in indexes)

    # ── Document Upload ───────────────────────────────────────────────

    def upload_documents(self, documents: list) -> dict:
        """Upload documents to the search index."""
        if self._fallback_mode:
            logger.info(f"[Fallback] Would upload {len(documents)} documents")
            return {"status": "fallback", "count": len(documents)}

        requests = self._import_requests()
        
        batch = {
            "value": [
                {"@search.action": "upload", **doc}
                for doc in documents
            ]
        }

        response = requests.post(
            self._url(f"indexes('{self.index_name}')/docs/index"),
            headers=self._headers,
            json=batch
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Uploaded {len(documents)} documents, status: {result.get('status', 'unknown')}")
        return result

    def ingest_knowledge_base(self, kb_dir: str = None) -> dict:
        """Parse markdown files from knowledge_base/ and upload as search documents."""
        import os as _os
        
        if kb_dir is None:
            kb_dir = _os.path.join(
                _os.path.dirname(_os.path.dirname(__file__)),
                "knowledge_base"
            )

        documents = []
        for filename in _os.listdir(kb_dir):
            if not filename.endswith(".md"):
                continue

            cert_id = filename.replace("_guide.md", "").upper().replace("_SYNTHETIC", "")
            filepath = _os.path.join(kb_dir, filename)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            sections = self._chunk_content(content, cert_id)
            for section in sections:
                doc_id = hashlib.md5(
                    f"{cert_id}:{section['section']}".encode()
                ).hexdigest()[:16]
                documents.append({
                    "id": doc_id,
                    "cert_id": cert_id,
                    "title": f"{cert_id} - {section['section']}",
                    "content": section["content"],
                    "section": section["section"],
                    "skill_domain": section.get("skill_domain", "General"),
                    "source_file": filename
                })

        logger.info(f"Parsed {len(documents)} documents from {kb_dir}")
        return self.upload_documents(documents)

    def _chunk_content(self, content: str, cert_id: str) -> list:
        """Split markdown content into searchable sections at ## and ### level."""
        sections = []
        current_section = "Overview"
        current_content = []
        current_skill = "General"

        for line in content.split("\n"):
            if line.startswith("### "):
                if current_content:
                    sections.append({
                        "section": current_section,
                        "content": "\n".join(current_content).strip(),
                        "skill_domain": current_skill
                    })
                current_section = line.replace("### ", "").strip()
                current_content = []
                current_skill = self._infer_skill_domain(current_section, cert_id)
            elif line.startswith("## "):
                if current_content:
                    sections.append({
                        "section": current_section,
                        "content": "\n".join(current_content).strip(),
                        "skill_domain": current_skill
                    })
                current_section = line.replace("## ", "").strip()
                current_content = []
                current_skill = self._infer_skill_domain(current_section, cert_id)
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "section": current_section,
                "content": "\n".join(current_content).strip(),
                "skill_domain": current_skill
            })

        return sections

    def _infer_skill_domain(self, section_title: str, cert_id: str) -> str:
        """Infer skill domain from section title."""
        title_lower = section_title.lower()
        if any(k in title_lower for k in ["network", "vnet", "dns", "load balancer", "gateway"]):
            return "Networking"
        if any(k in title_lower for k in ["security", "identity", "access", "rbac", "compliance"]):
            return "Security & Identity"
        if any(k in title_lower for k in ["storage", "blob", "file", "disk"]):
            return "Storage"
        if any(k in title_lower for k in ["compute", "vm", "container", "function", "app service"]):
            return "Compute"
        if any(k in title_lower for k in ["monitor", "alert", "log", "metric"]):
            return "Monitoring"
        if any(k in title_lower for k in ["cost", "pricing", "sla", "lifecycle"]):
            return "Management & Governance"
        if any(k in title_lower for k in ["devops", "pipeline", "ci/cd", "deploy"]):
            return "DevOps"
        if any(k in title_lower for k in ["api", "develop", "code", "sdk"]):
            return "Development"
        return "General"

    # ── Query ─────────────────────────────────────────────────────────

    def _normalize_cert_id(self, cert_id: str) -> str:
        """Normalize cert_id to match indexed format (uppercase, no dashes)."""
        return cert_id.upper().replace("-", "")

    def query(
        self,
        query_text: str,
        cert_id: str = None,
        top_k: int = 5,
        use_semantic: bool = True
    ) -> list:
        """Query the knowledge base with optional semantic ranking.
        
        Auto-selects simple vs semantic search based on query length.
        Short queries (<=3 words) use keyword search for precision.
        Longer queries use semantic ranking for relevance.
        """
        if self._fallback_mode:
            return self._fallback_query(query_text, cert_id, top_k)

        requests = self._import_requests()
        
        word_count = len(query_text.split())
        effective_semantic = use_semantic and word_count > 3
        
        search_body = {
            "search": query_text,
            "top": top_k,
            "select": "id,cert_id,title,content,section,skill_domain,source_file",
            "queryType": "semantic" if effective_semantic else "simple",
        }

        if effective_semantic:
            search_body["semanticConfiguration"] = "crucible-semantic-config"
            search_body["captions"] = "extractive|highlight-true"
            search_body["answers"] = "extractive"

        if cert_id:
            normalized = self._normalize_cert_id(cert_id)
            search_body["filter"] = f"cert_id eq '{normalized}'"

        response = requests.post(
            self._url(f"indexes('{self.index_name}')/docs/search"),
            headers=self._headers,
            json=search_body
        )
        response.raise_for_status()
        result = response.json()

        results = []
        for hit in result.get("value", []):
            reranker_score = hit.get("@search.rerankerScore", 0)
            caption = ""
            if "@search.captions" in hit and hit["@search.captions"]:
                caption = hit["@search.captions"][0].get("text", "")
            
            results.append({
                "id": hit.get("id", ""),
                "cert_id": hit.get("cert_id", ""),
                "title": hit.get("title", ""),
                "content": hit.get("content", ""),
                "section": hit.get("section", ""),
                "skill_domain": hit.get("skill_domain", ""),
                "source_file": hit.get("source_file", ""),
                "reranker_score": reranker_score,
                "caption": caption
            })

        logger.info(f"Query returned {len(results)} results for: {query_text[:60]}...")
        return results

    def get_answer(self, query_text: str, cert_id: str = None) -> Optional[str]:
        """Get a semantic answer to a question-like query."""
        if self._fallback_mode:
            return None

        requests = self._import_requests()
        
        search_body = {
            "search": query_text,
            "top": 3,
            "queryType": "semantic",
            "semanticConfiguration": "crucible-semantic-config",
            "answers": "extractive",
            "select": "id,cert_id,title,content,section,skill_domain,source_file"
        }

        if cert_id:
            normalized = self._normalize_cert_id(cert_id)
            search_body["filter"] = f"cert_id eq '{normalized}'"

        response = requests.post(
            self._url(f"indexes('{self.index_name}')/docs/search"),
            headers=self._headers,
            json=search_body
        )
        response.raise_for_status()
        result = response.json()

        answers = result.get("@search.answers", [])
        if answers and answers[0].get("score", 0) > 0.7:
            return answers[0].get("text", "")
        return None

    # ── Fallback Mode ─────────────────────────────────────────────────

    def _fallback_query(self, query_text: str, cert_id: str = None, top_k: int = 5) -> list:
        """Simple keyword-based fallback when Azure AI Search is unavailable."""
        import os as _os
        
        kb_dir = _os.path.join(
            _os.path.dirname(_os.path.dirname(__file__)),
            "knowledge_base"
        )
        
        results = []
        query_lower = query_text.lower()
        query_words = set(query_lower.split())

        for filename in _os.listdir(kb_dir):
            if not filename.endswith(".md"):
                continue

            file_cert = filename.replace("_guide.md", "").upper().replace("_SYNTHETIC", "")
            if cert_id and file_cert != self._normalize_cert_id(cert_id):
                continue

            filepath = _os.path.join(kb_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            score = sum(1 for word in query_words if word in content.lower())
            if score > 0:
                results.append({
                    "id": f"fallback-{file_cert}",
                    "cert_id": file_cert,
                    "title": f"{file_cert} Guide",
                    "content": content[:2000],
                    "section": "Full Document",
                    "skill_domain": "General",
                    "source_file": filename,
                    "reranker_score": score,
                    "caption": ""
                })

        results.sort(key=lambda x: x["reranker_score"], reverse=True)
        return results[:top_k]

    # ── Setup Helper ──────────────────────────────────────────────────

    def ensure_indexed(self, kb_dir: str = None) -> dict:
        """Create index and ingest documents if not already done."""
        if self._fallback_mode:
            logger.info("[Fallback] Using local file search")
            return {"status": "fallback"}

        if not self.index_exists():
            self.create_index()
        
        return self.ingest_knowledge_base(kb_dir)
