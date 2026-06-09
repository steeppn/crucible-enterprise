import json
import logging
import requests
from typing import Optional

logger = logging.getLogger("crucible.services.mcp")

class MCPClient:
    """Microsoft Learn MCP Server client.
    
    Connects to the public Microsoft Learn MCP endpoint via Streamable HTTP.
    Discovers tools dynamically and invokes them for documentation retrieval.
    
    Endpoint: https://learn.microsoft.com/api/mcp
    No authentication required.
    """

    MCP_ENDPOINT = "https://learn.microsoft.com/api/mcp"

    def __init__(self):
        self._session_id: Optional[str] = None
        self._tools: list = []
        self._initialized = False

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        return headers

    def _send(self, method: str, params: dict = None) -> dict:
        """Send a JSON-RPC 2.0 request to the MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }

        try:
            response = requests.post(
                self.MCP_ENDPOINT,
                headers=self._headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                
                if "text/event-stream" in content_type:
                    return self._parse_sse(response.text)
                
                return response.json()
            
            logger.warning(f"MCP request failed: {response.status_code} {response.text[:200]}")
            return {"error": f"HTTP {response.status_code}", "result": None}
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"MCP connection error: {e}")
            return {"error": str(e), "result": None}

    def _parse_sse(self, text: str) -> dict:
        """Parse SSE response into JSON."""
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("data: "):
                try:
                    return json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
        return {"error": "Failed to parse SSE", "result": None}

    def initialize(self) -> bool:
        """Initialize the MCP session and discover available tools."""
        if self._initialized:
            return True

        result = self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "crucible-enterprise", "version": "1.0.0"}
        })

        if "result" in result:
            self._session_id = result.get("result", {}).get("sessionId")
            if not self._session_id:
                self._session_id = result.get("sessionId")
            self._initialized = True
            
            self._send("notifications/initialized", {})
            
            tools_result = self._send("tools/list")
            if "result" in tools_result:
                tools_data = tools_result["result"]
                if isinstance(tools_data, dict):
                    self._tools = tools_data.get("tools", [])
                elif isinstance(tools_data, list):
                    self._tools = tools_data
                logger.info(f"MCP initialized with {len(self._tools)} tools: {[t.get('name', t) for t in self._tools]}")
                return True

        logger.warning("MCP initialization failed, will use fallback")
        return False

    def search_docs(self, query: str, top_k: int = 5) -> list:
        """Search Microsoft Learn documentation."""
        if not self._initialized:
            self.initialize()

        result = self._send("tools/call", {
            "name": "microsoft_docs_search",
            "arguments": {"query": query}
        })

        if "result" in result:
            result_data = result["result"]
            if isinstance(result_data, dict):
                content = result_data.get("content", [])
                if content:
                    text = content[0].get("text", "")
                    return self._parse_search_results(text, top_k)
                
                structured = result_data.get("structuredContent", {})
                if structured:
                    return self._parse_structured_results(structured, top_k)

        logger.warning(f"MCP search failed for: {query[:60]}...")
        return []

    def fetch_doc(self, url: str) -> Optional[str]:
        """Fetch full documentation page as markdown."""
        if not self._initialized:
            self.initialize()

        result = self._send("tools/call", {
            "name": "microsoft_docs_fetch",
            "arguments": {"url": url}
        })

        if "result" in result:
            result_data = result["result"]
            if isinstance(result_data, dict):
                content = result_data.get("content", [])
                if content:
                    return content[0].get("text", "")
        return None

    def search_code_samples(self, query: str, language: str = None) -> list:
        """Search for official Microsoft code samples."""
        if not self._initialized:
            self.initialize()

        args = {"query": query}
        if language:
            args["language"] = language

        result = self._send("tools/call", {
            "name": "microsoft_code_sample_search",
            "arguments": args
        })

        if "result" in result:
            result_data = result["result"]
            if isinstance(result_data, dict):
                content = result_data.get("content", [])
                if content:
                    text = content[0].get("text", "")
                    return self._parse_code_samples(text)
                
                structured = result_data.get("structuredContent", {})
                if structured:
                    return self._parse_structured_code_samples(structured)
        return []

    def _parse_search_results(self, text: str, top_k: int = 5) -> list:
        """Parse MCP search result text into structured results.
        
        The text field contains a JSON string with a 'results' array.
        """
        try:
            data = json.loads(text)
            results = data.get("results", [])
            parsed = []
            for r in results[:top_k]:
                parsed.append({
                    "title": r.get("title", ""),
                    "url": r.get("contentUrl", r.get("url", "")),
                    "content": r.get("content", "")[:500],
                    "summary": r.get("content", "")[:200]
                })
            return parsed
        except json.JSONDecodeError:
            pass

        results = []
        lines = text.strip().split("\n")
        current = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Title:") or line.startswith("- Title:"):
                if current.get("title"):
                    results.append(current)
                current = {"title": line.split(":", 1)[1].strip() if ":" in line else line}
            elif line.startswith("URL:") or line.startswith("- URL:"):
                current["url"] = line.split(":", 1)[1].strip() if ":" in line else line
            elif line.startswith("Summary:") or line.startswith("- Summary:"):
                current["summary"] = line.split(":", 1)[1].strip() if ":" in line else line
            elif line.startswith("Content:") or line.startswith("- Content:"):
                current["content"] = line.split(":", 1)[1].strip() if ":" in line else line

        if current.get("title"):
            results.append(current)

        return results[:top_k]

    def _parse_structured_results(self, structured: dict, top_k: int = 5) -> list:
        """Parse structuredContent from MCP response."""
        results = structured.get("results", [])
        parsed = []
        for r in results[:top_k]:
            parsed.append({
                "title": r.get("title", ""),
                "url": r.get("contentUrl", r.get("url", "")),
                "content": r.get("content", "")[:500],
                "summary": r.get("content", "")[:200]
            })
        return parsed

    def _parse_code_samples(self, text: str) -> list:
        """Parse MCP code sample results."""
        try:
            data = json.loads(text)
            samples = data.get("results", data.get("samples", []))
            parsed = []
            for s in samples:
                parsed.append({
                    "title": s.get("title", ""),
                    "url": s.get("contentUrl", s.get("url", "")),
                    "language": s.get("language", ""),
                    "content": s.get("content", "")[:500]
                })
            return parsed
        except json.JSONDecodeError:
            pass

        samples = []
        lines = text.strip().split("\n")
        current = {}
        for line in lines:
            line = line.strip()
            if line.startswith("Title:") or line.startswith("- Title:"):
                if current.get("title"):
                    samples.append(current)
                current = {"title": line.split(":", 1)[1].strip() if ":" in line else line}
            elif line.startswith("URL:") or line.startswith("- URL:"):
                current["url"] = line.split(":", 1)[1].strip() if ":" in line else line
            elif line.startswith("Language:") or line.startswith("- Language:"):
                current["language"] = line.split(":", 1)[1].strip() if ":" in line else line

        if current.get("title"):
            samples.append(current)

        return samples

    def _parse_structured_code_samples(self, structured: dict) -> list:
        """Parse structuredContent for code samples."""
        samples = structured.get("results", structured.get("samples", []))
        parsed = []
        for s in samples:
            parsed.append({
                "title": s.get("title", ""),
                "url": s.get("contentUrl", s.get("url", "")),
                "language": s.get("language", ""),
                "content": s.get("content", "")[:500]
            })
        return parsed

    def get_available_tools(self) -> list:
        """Return list of available MCP tools."""
        return self._tools

    def is_available(self) -> bool:
        """Check if MCP server is reachable."""
        try:
            response = requests.post(
                self.MCP_ENDPOINT,
                headers=self._headers(),
                json={"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "crucible-enterprise", "version": "1.0.0"}
                }},
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
