"""
Servidor HTTP ligero para Cloud Run.
Expone el pipeline como API REST.
"""

import asyncio
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

from agents.orchestrator import Orchestrator


orch = Orchestrator()


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self._respond(200, {
                "service": "ARIGRA Agentic Sales System v2",
                "status": "running",
                "agents": 13,
                "phases": 4,
                "endpoints": {
                    "/": "Health check",
                    "/run": "POST - Run full pipeline",
                    "/phase/1": "POST - Run phase 1",
                    "/phase/2": "POST - Run phase 2",
                    "/phase/3": "POST - Run phase 3",
                    "/phase/4": "POST - Run phase 4 (insights)",
                    "/mark/reply": "POST - Mark reply",
                    "/mark/meeting": "POST - Mark meeting",
                    "/insights": "GET - Get learning insights",
                },
            })
        elif self.path == "/health":
            self._respond(200, {"status": "healthy"})
        elif self.path == "/insights":
            insights_path = orch.data_dir / "learning_insights.json"
            if insights_path.exists():
                data = json.loads(insights_path.read_text(encoding="utf-8"))
                self._respond(200, data)
            else:
                self._respond(404, {"error": "No insights yet"})
        else:
            self._respond(404, {"error": "Not found"})

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}

        if self.path == "/run":
            result = asyncio.run(orch.run_full_pipeline(
                query=body.get("query", "empresas tecnología Madrid"),
                max_results=body.get("max_results", 30),
                n_clusters=body.get("clusters", 4),
                dry_run=body.get("dry_run", True),
            ))
            self._respond(200, {
                "status": "completed",
                "scraped": result.total_scraped,
                "enriched": result.total_enriched,
                "validated": result.total_validated,
                "clustered": result.total_clustered,
                "emails_sent": result.total_emails_sent,
            })

        elif self.path.startswith("/phase/"):
            phase = int(self.path.split("/")[-1])
            result = self._run_phase(phase, body)
            self._respond(200, result)

        elif self.path == "/mark/reply":
            name = body.get("company_name", "")
            sentiment = body.get("sentiment", "neutral")
            orch.mark_replied(name, sentiment)
            self._respond(200, {"status": "ok", "company": name})

        elif self.path == "/mark/meeting":
            name = body.get("company_name", "")
            orch.mark_meeting(name)
            self._respond(200, {"status": "ok", "company": name})

        elif self.path == "/mark/converted":
            name = body.get("company_name", "")
            orch.mark_converted(name)
            self._respond(200, {"status": "ok", "company": name})

        else:
            self._respond(404, {"error": "Not found"})

    def _run_phase(self, phase: int, body: dict) -> dict:
        if phase == 1:
            companies = asyncio.run(orch.run_phase_1(
                query=body.get("query", "empresas tecnología Madrid"),
                max_results=body.get("max_results", 30),
            ))
            return {"phase": 1, "companies": len(companies)}
        elif phase == 2:
            companies, profiles = asyncio.run(orch.run_phase_2(
                n_clusters=body.get("clusters", 4),
            ))
            return {"phase": 2, "companies": len(companies), "clusters": len(profiles)}
        elif phase == 3:
            drafts = asyncio.run(orch.run_phase_3(
                dry_run=body.get("dry_run", True),
            ))
            return {"phase": 3, "drafts": len(drafts)}
        elif phase == 4:
            insights = asyncio.run(orch.run_phase_4())
            return {"phase": 4, "insights": insights}
        return {"error": "Invalid phase"}

    def _respond(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode("utf-8"))


def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"ARIGRA Agentic Sales Server running on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
