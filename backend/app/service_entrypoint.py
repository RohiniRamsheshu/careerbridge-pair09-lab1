"""Incremental independently runnable domain boundaries.

The Lab 1-compatible API remains in ``main.py``. These processes reuse that
business implementation but expose only the route families owned by one domain
so the monolith can be decomposed without copying SQL, auth, or agent logic.
They are deployment boundaries, not a claim that all persistence has already
been split into six databases.
"""

import argparse
import logging

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app import config
from backend.app.main import app as compatibility_app

logger = logging.getLogger("careerbridge.domain_service")

SERVICE_PREFIXES = {
    "student": ("/auth", "/student", "/dashboard/student", "/saved-items"),
    "company": ("/auth", "/company", "/dashboard/company", "/search/students"),
    "job": ("/jobs", "/search/companies"),
    "application": ("/applications",),
    "event": ("/events",),
    "assistant": ("/assistant",),
}


def create_service_app(service_name: str) -> FastAPI:
    if service_name not in SERVICE_PREFIXES:
        raise ValueError(f"Unsupported domain service: {service_name}")

    service_app = FastAPI(title=f"CareerBridge {service_name.title()} Service")

    @service_app.get("/health")
    def service_health():
        return {
            "status": "ok",
            "service": service_name,
            "port": config.domain_service_port(service_name),
        }

    @service_app.get("/service-info")
    def service_info():
        return {
            "service": service_name,
            "owned_prefixes": list(SERVICE_PREFIXES[service_name]),
            "compatibility_api": "backend.app.main",
        }

    @service_app.middleware("http")
    async def enforce_boundary(request: Request, call_next):
        path = request.url.path
        if path in {"/health", "/service-info"} or any(
            path == prefix or path.startswith(prefix + "/")
            for prefix in SERVICE_PREFIXES[service_name]
        ):
            return await call_next(request)
        return JSONResponse(
            status_code=404,
            content={"detail": f"Route is not owned by the {service_name} service"},
        )

    service_app.mount("/", compatibility_app)
    return service_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", choices=sorted(SERVICE_PREFIXES), required=True)
    args = parser.parse_args()
    service_name = args.service
    uvicorn.run(
        create_service_app(service_name),
        host="0.0.0.0",
        port=config.domain_service_port(service_name),
    )


if __name__ == "__main__":
    main()
