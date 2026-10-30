import sys
from pathlib import Path

# Add project root to sys.path so app and core modules resolve cleanly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app import app as original_app

class VercelPathFixer:
    """
    Normalizes ASGI request paths when Vercel routes traffic through /api/index.
    Strips leading /api/index prefix so all FastAPI routes match naturally.
    """
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "")
            if path in ("/api/index", "/api/index/", "/api", "/api/"):
                scope["path"] = "/"
            elif path.startswith("/api/index/"):
                scope["path"] = path[len("/api/index"):]
            elif path.startswith("/api/") and not path.startswith("/api/v1"):
                scope["path"] = path[len("/api"):]
        await self.asgi_app(scope, receive, send)

    def __getattr__(self, name):
        return getattr(self.asgi_app, name)

app = VercelPathFixer(original_app)
