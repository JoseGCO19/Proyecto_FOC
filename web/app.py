import json
import os
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Asegurar que el directorio raíz del proyecto esté en sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.lp_parser import LPParser
from core.dual_simplex import DualSimplexSolver
from core.fraction_utils import format_fraction

WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class DualSimplexHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path in ["/", "/index.html"]:
            self.serve_file(os.path.join(WEB_DIR, "templates", "index.html"), "text/html")
        elif path.startswith("/static/css/"):
            self.serve_file(os.path.join(WEB_DIR, "static", "css", path.replace("/static/css/", "")), "text/css")
        elif path.startswith("/static/js/"):
            self.serve_file(os.path.join(WEB_DIR, "static", "js", path.replace("/static/js/", "")), "application/javascript")
        elif path == "/api/examples":
            examples = {
                "estandar": """MAX z = -3 x1 - 2 x2
s.t.
x1 + 2 x2 >= 6
2 x1 + x2 >= 8
x1, x2 >= 0""",
                "infactible": """MAX z = -x1 - x2
s.t.
-x1 - x2 <= -5
x1 + x2 <= 2
x1, x2 >= 0""",
                "tres_vars": """MAX z = -3 x1 - 4 x2 - 1 x3
s.t.
-x1 - 2 x2 - x3 <= -6
-2 x1 - x2 - 3 x3 <= -8
x1, x2, x3 >= 0"""
            }
            self.send_json_response(examples)
        else:
            self.send_error(404, "Página no encontrada")

    def do_POST(self):
        if self.path == "/api/solve":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            
            try:
                data = json.loads(body)
                mode = data.get("mode", "fraction")
                pivot_rule = data.get("pivot_rule", "bland")

                if "text" in data and data["text"].strip():
                    dictionary = LPParser.parse_text_algebraic(data["text"])
                elif "json_lp" in data:
                    dictionary = LPParser.from_json_dict(data["json_lp"])
                else:
                    raise ValueError("No se proporcionaron datos de entrada válidos.")

                solver = DualSimplexSolver(dictionary, pivot_rule=pivot_rule)
                history = solver.solve()

                steps_data = [step.to_dict(mode=mode) for step in history]
                
                response_data = {
                    "success": True,
                    "mode": mode,
                    "total_steps": len(steps_data),
                    "steps": steps_data,
                    "final_status": history[-1].status if history else "UNKNOWN"
                }
                self.send_json_response(response_data)

            except Exception as e:
                self.send_json_response({"success": False, "error": str(e)}, status_code=400)
        else:
            self.send_error(404, "Endpoint no encontrado")

    def serve_file(self, filepath: str, content_type: str):
        if not os.path.exists(filepath):
            self.send_error(404, "Archivo no encontrado")
            return
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    def send_json_response(self, data: dict, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


# Para compatibilidad con FastAPI si se ejecuta uvicorn
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel

    app = FastAPI(title="Simplex Dual Solver")

    app.mount("/static", StaticFiles(directory=os.path.join(WEB_DIR, "static")), name="static")

    class SolveRequest(BaseModel):
        text: str = ""
        json_lp: dict = {}
        mode: str = "fraction"
        pivot_rule: str = "bland"

    @app.get("/", response_class=HTMLResponse)
    def read_root():
        with open(os.path.join(WEB_DIR, "templates", "index.html"), "r", encoding="utf-8") as f:
            return f.read()

    @app.post("/api/solve")
    def api_solve(req: SolveRequest):
        try:
            if req.text.strip():
                dictionary = LPParser.parse_text_algebraic(req.text)
            elif req.json_lp:
                dictionary = LPParser.from_json_dict(req.json_lp)
            else:
                raise ValueError("Entrada vacía.")

            solver = DualSimplexSolver(dictionary, pivot_rule=req.pivot_rule)
            history = solver.solve()
            steps_data = [step.to_dict(mode=req.mode) for step in history]

            return {
                "success": True,
                "mode": req.mode,
                "total_steps": len(steps_data),
                "steps": steps_data,
                "final_status": history[-1].status if history else "UNKNOWN"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

except ImportError:
    app = None


def run_standalone_server(port: int = 8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DualSimplexHandler)
    print(f"Servidor Web iniciado en http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_standalone_server()
