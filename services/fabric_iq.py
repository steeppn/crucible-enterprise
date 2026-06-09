import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("crucible.services.fabric_iq")

class FabricIQClient:
    """Simulated Fabric IQ client for semantic ontology queries.
    
    In production, this would connect to Microsoft Fabric via the Ontology
    MCP endpoint. For the hackathon demo, it simulates ontology traversal
    using synthetic data structured as business entities and relationships.
    
    This layer enables agents to reason over:
    - Certification prerequisites and dependency chains
    - Role-to-certification mappings
    - Skill overlap between certifications
    - Learner progression paths
    - Team readiness analytics
    """

    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data"
            )
        self._ontology = self._load_ontology(data_dir)
        self._learner_data = self._load_learner_data(data_dir)
        self._build_relationships()

    def _load_ontology(self, data_dir: str) -> dict:
        """Load certification semantic model as ontology seed."""
        model_file = os.path.join(data_dir, "certification_semantic_model.json")
        if os.path.exists(model_file):
            with open(model_file, "r") as f:
                return json.load(f)
        logger.warning("certification_semantic_model.json not found, using empty ontology")
        return {"certifications": [], "roles": []}

    def _load_learner_data(self, data_dir: str) -> list:
        """Load synthetic learner performance data."""
        learner_file = os.path.join(data_dir, "learner_performance.json")
        if os.path.exists(learner_file):
            with open(learner_file, "r") as f:
                return json.load(f)
        return []

    def _build_relationships(self):
        """Build derived relationships from ontology data."""
        self._cert_by_id = {}
        for cert in self._ontology.get("certifications", []):
            self._cert_by_id[cert["id"]] = cert

        self._role_by_name = {}
        for role in self._ontology.get("roles", []):
            self._role_by_name[role["role"]] = role

        self._skill_index = {}
        for cert in self._ontology.get("certifications", []):
            for skill in cert.get("skills", []):
                if skill not in self._skill_index:
                    self._skill_index[skill] = []
                self._skill_index[skill].append(cert["id"])

    # ── Certification Queries ─────────────────────────────────────────

    def get_cert_details(self, cert_id: str) -> Optional[dict]:
        """Get full certification details from ontology."""
        cert = self._cert_by_id.get(cert_id.upper().replace("-", ""))
        if not cert:
            for c in self._ontology.get("certifications", []):
                if c["id"].upper().replace("-", "") == cert_id.upper().replace("-", ""):
                    cert = c
                    break
        
        if not cert:
            return None

        return {
            "id": cert["id"],
            "name": cert.get("name", cert["id"]),
            "skills": cert.get("skills", []),
            "recommended_hours": cert.get("recommended_hours", 40),
            "prerequisites": cert.get("prerequisites", []),
            "difficulty": cert.get("difficulty", "Associate"),
            "dependent_certs": self._get_dependent_certs(cert["id"])
        }

    def get_cert_prerequisites(self, cert_id: str, include_chain: bool = True) -> list:
        """Get prerequisite certification chain.
        
        Simulates Fabric IQ ontology traversal for dependency resolution.
        """
        cert = self.get_cert_details(cert_id)
        if not cert:
            return []

        prerequisites = cert.get("prerequisites", [])
        
        if include_chain:
            all_prereqs = list(prerequisites)
            for prereq_id in prerequisites:
                chain = self.get_cert_prerequisites(prereq_id, include_chain=True)
                for c in chain:
                    if c not in all_prereqs:
                        all_prereqs.append(c)
            return all_prereqs

        return prerequisites

    def get_dependent_certs(self, cert_id: str) -> list:
        """Get certifications that depend on this one."""
        dependents = []
        for cert in self._ontology.get("certifications", []):
            prereqs = cert.get("prerequisites", [])
            if cert_id in prereqs:
                dependents.append(cert["id"])
        return dependents

    def _get_dependent_certs(self, cert_id: str) -> list:
        """Internal: get certifications that list this as a prerequisite."""
        return self.get_dependent_certs(cert_id)

    # ── Role Queries ──────────────────────────────────────────────────

    def get_role_cert_mapping(self, role: str) -> dict:
        """Get certification mapping for a role.
        
        Simulates Fabric IQ entity relationship query.
        """
        role_data = self._role_by_name.get(role)
        if not role_data:
            return {
                "role": role,
                "primary_cert": None,
                "secondary_cert": None,
                "recommended_path": self._suggest_path_for_role(role)
            }

        return {
            "role": role_data["role"],
            "primary_cert": role_data.get("primary_cert"),
            "secondary_cert": role_data.get("secondary_cert"),
            "recommended_path": self._build_recommended_path(
                role_data.get("primary_cert"),
                role_data.get("secondary_cert")
            )
        }

    def _suggest_path_for_role(self, role: str) -> list:
        """Suggest a certification path for an unknown role."""
        role_lower = role.lower()
        if "cloud" in role_lower:
            return ["AZ-900", "AZ-104", "AZ-305"]
        if "network" in role_lower:
            return ["AZ-900", "AZ-104", "AZ-700"]
        if "devops" in role_lower:
            return ["AZ-900", "AZ-104", "AZ-400"]
        if "develop" in role_lower:
            return ["AZ-900", "AZ-204"]
        if "data" in role_lower:
            return ["DP-900", "DP-203"]
        if "security" in role_lower:
            return ["SC-900", "SC-200"]
        return ["AZ-900"]

    def _build_recommended_path(self, primary: str = None, secondary: str = None) -> list:
        """Build a recommended certification path."""
        path = []
        if primary:
            prereqs = self.get_cert_prerequisites(primary, include_chain=True)
            path.extend(prereqs)
            if primary not in path:
                path.append(primary)
        if secondary and secondary not in path:
            path.append(secondary)
        return path

    # ── Skill Analysis ────────────────────────────────────────────────

    def get_skill_overlap(self, cert_a: str, cert_b: str) -> dict:
        """Get skill overlap between two certifications.
        
        Simulates Fabric IQ semantic relationship analysis.
        """
        cert_a_data = self.get_cert_details(cert_a)
        cert_b_data = self.get_cert_details(cert_b)

        if not cert_a_data or not cert_b_data:
            return {"cert_a": cert_a, "cert_b": cert_b, "overlap": [], "overlap_pct": 0}

        skills_a = set(cert_a_data.get("skills", []))
        skills_b = set(cert_b_data.get("skills", []))
        
        overlap = skills_a & skills_b
        all_skills = skills_a | skills_b
        
        overlap_pct = len(overlap) / len(all_skills) if all_skills else 0

        return {
            "cert_a": cert_a,
            "cert_b": cert_b,
            "skills_a": list(skills_a),
            "skills_b": list(skills_b),
            "overlap": list(overlap),
            "unique_to_a": list(skills_a - skills_b),
            "unique_to_b": list(skills_b - skills_a),
            "overlap_pct": round(overlap_pct, 2)
        }

    def get_certs_by_skill(self, skill: str) -> list:
        """Get all certifications that include a specific skill."""
        return self._skill_index.get(skill, [])

    def get_all_skills(self) -> list:
        """Get all unique skills across all certifications."""
        return list(self._skill_index.keys())

    # ── Learner Analytics ─────────────────────────────────────────────

    def get_learner_readiness(self, learner_id: str) -> dict:
        """Get readiness assessment for a learner.
        
        Simulates Fabric IQ analytics over learner performance data.
        """
        learner = None
        for l in self._learner_data:
            if l.get("learner_id") == learner_id:
                learner = l
                break

        if not learner:
            return {
                "learner_id": learner_id,
                "readiness_score": 0,
                "status": "not_found",
                "recommendation": "No data available"
            }

        score = learner.get("practice_score_avg", 0)
        hours = learner.get("hours_studied", 0)
        outcome = learner.get("exam_outcome", "Unknown")

        cert = self.get_cert_details(learner.get("certification", ""))
        recommended_hours = cert.get("recommended_hours", 40) if cert else 40

        hours_ratio = min(hours / recommended_hours, 1.0)
        score_component = score * 0.6
        hours_component = hours_ratio * 100 * 0.4
        readiness_score = round(score_component + hours_component, 1)

        if readiness_score >= 80:
            recommendation = "Ready for exam"
            status = "ready"
        elif readiness_score >= 60:
            recommendation = "Needs 1-2 more weeks of study"
            status = "nearly_ready"
        else:
            recommendation = "Needs significant additional preparation"
            status = "not_ready"

        return {
            "learner_id": learner_id,
            "role": learner.get("role", "Unknown"),
            "certification": learner.get("certification", "Unknown"),
            "practice_score": score,
            "hours_studied": hours,
            "recommended_hours": recommended_hours,
            "hours_gap": max(0, recommended_hours - hours),
            "readiness_score": readiness_score,
            "exam_outcome": outcome,
            "status": status,
            "recommendation": recommendation
        }

    def get_team_analytics(self, cert_id: str = None) -> dict:
        """Get team-level analytics for manager insights.
        
        Simulates Fabric IQ aggregated analytics.
        """
        learners = self._learner_data
        if cert_id:
            learners = [l for l in learners if l.get("certification", "").upper().replace("-", "") == cert_id.upper().replace("-", "")]

        if not learners:
            return {
                "total_learners": 0,
                "avg_readiness": 0,
                "pass_rate": 0,
                "avg_hours_studied": 0,
                "risk_flags": []
            }

        readiness_scores = []
        for l in learners:
            readiness = self.get_learner_readiness(l["learner_id"])
            readiness_scores.append(readiness["readiness_score"])

        avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0
        pass_count = sum(1 for l in learners if l.get("exam_outcome") == "Pass")
        pass_rate = pass_count / len(learners) if learners else 0
        avg_hours = sum(l.get("hours_studied", 0) for l in learners) / len(learners)

        risk_flags = []
        overconfident = [l for l in learners if l.get("practice_score_avg", 0) < 60 and l.get("hours_studied", 0) < 15]
        if overconfident:
            risk_flags.append({
                "risk_type": "underprepared",
                "description": "Learners with low study hours and low practice scores",
                "affected_count": len(overconfident)
            })

        high_meeting = [l for l in learners if l.get("practice_score_avg", 0) >= 70 and l.get("exam_outcome") == "Fail"]
        if high_meeting:
            risk_flags.append({
                "risk_type": "knowledge_gap",
                "description": "Learners with good practice scores but failed exams",
                "affected_count": len(high_meeting)
            })

        return {
            "total_learners": len(learners),
            "avg_readiness": round(avg_readiness, 1),
            "pass_rate": round(pass_rate, 2),
            "avg_hours_studied": round(avg_hours, 1),
            "risk_flags": risk_flags,
            "cert_breakdown": self._cert_breakdown(learners)
        }

    def _cert_breakdown(self, learners: list) -> dict:
        """Break down learners by certification."""
        breakdown = {}
        for l in learners:
            cert = l.get("certification", "Unknown")
            if cert not in breakdown:
                breakdown[cert] = {"count": 0, "pass": 0, "fail": 0}
            breakdown[cert]["count"] += 1
            if l.get("exam_outcome") == "Pass":
                breakdown[cert]["pass"] += 1
            else:
                breakdown[cert]["fail"] += 1
        return breakdown

    # ── Recommendation Engine ─────────────────────────────────────────

    def recommend_next_cert(self, role: str, completed_certs: list) -> list:
        """Recommend next certification based on role and completed certs.
        
        Simulates Fabric IQ ontology-based recommendation.
        """
        role_mapping = self.get_role_cert_mapping(role)
        recommended_path = role_mapping.get("recommended_path", [])
        
        completed_set = set(c.upper().replace("-", "") for c in completed_certs)
        
        recommendations = []
        for cert_id in recommended_path:
            if cert_id.upper().replace("-", "") not in completed_set:
                cert = self.get_cert_details(cert_id)
                if cert:
                    recommendations.append({
                        "cert_id": cert["id"],
                        "name": cert["name"],
                        "difficulty": cert["difficulty"],
                        "recommended_hours": cert["recommended_hours"],
                        "prerequisites_met": self._prereqs_met(cert["id"], completed_set),
                        "reason": f"Next step in {role} certification path"
                    })

        if not recommendations:
            all_certs = self._ontology.get("certifications", [])
            for cert in all_certs:
                if cert["id"].upper().replace("-", "") not in completed_set:
                    recommendations.append({
                        "cert_id": cert["id"],
                        "name": cert.get("name", cert["id"]),
                        "difficulty": cert.get("difficulty", "Associate"),
                        "recommended_hours": cert.get("recommended_hours", 40),
                        "prerequisites_met": self._prereqs_met(cert["id"], completed_set),
                        "reason": "Alternative certification path"
                    })
                    break

        return recommendations

    def _prereqs_met(self, cert_id: str, completed_set: set) -> bool:
        """Check if all prerequisites for a cert are completed."""
        prereqs = self.get_cert_prerequisites(cert_id, include_chain=True)
        return all(p.upper().replace("-", "") in completed_set for p in prereqs)

    # ── Ontology Summary ──────────────────────────────────────────────

    def get_ontology_summary(self) -> dict:
        """Get a summary of the ontology structure."""
        return {
            "total_certifications": len(self._ontology.get("certifications", [])),
            "total_roles": len(self._ontology.get("roles", [])),
            "total_skills": len(self._skill_index),
            "certifications": [c["id"] for c in self._ontology.get("certifications", [])],
            "roles": [r["role"] for r in self._ontology.get("roles", [])],
            "skills": list(self._skill_index.keys())
        }
