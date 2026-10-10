"""
FastAPI Web Server & API Gateway Entrypoint for Road Damage Detection and Severity Assessment.
Delegates to the modular Microservices Architecture (services.api_gateway.app).
"""

from services.api_gateway.app import SAMPLES_METADATA, app
from services.common.config import GATEWAY_HOST, GATEWAY_PORT, SERVICE_REGISTRY

__all__ = ["app", "SAMPLES_METADATA"]

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 72)
    print("🚀 ROADVISION AI - MICROSERVICES API GATEWAY & WEB APPLICATION")
    print("=" * 72)
    print(f"👉 Web UI & API Gateway : http://127.0.0.1:{GATEWAY_PORT}")
    print(f"👉 Gateway OpenAPI Docs : http://127.0.0.1:{GATEWAY_PORT}/docs")
    print("   Mounted Microservice Endpoints:")
    print(f"   • Detection Service     : http://127.0.0.1:{GATEWAY_PORT}/services/detection/docs")
    print(f"   • Severity Service      : http://127.0.0.1:{GATEWAY_PORT}/services/severity/docs")
    print(f"   • Visualization Service : http://127.0.0.1:{GATEWAY_PORT}/services/visualization/docs")
    print(f"   • Reporting Service     : http://127.0.0.1:{GATEWAY_PORT}/services/reporting/docs")
    print("=" * 72 + "\n")
    uvicorn.run("web_server:app", host=GATEWAY_HOST, port=GATEWAY_PORT, reload=False)
