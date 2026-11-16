"""Environment-derived deployment settings for Pair 09.

The defaults preserve the Lab 1 local setup. Lab 2 infrastructure can override
these values through environment variables without scattering pair-specific
constants through application code.
"""

import os


PAIR = os.getenv("PAIR", "09")
PORT_BASE = int(os.getenv("PORT_BASE", "9090"))
RESOURCE_PREFIX = os.getenv("RESOURCE_PREFIX", f"p{PAIR}")
KAFKA_PREFIX = os.getenv("KAFKA_PREFIX", RESOURCE_PREFIX)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "0") == "1"
KAFKA_PUBLISH_TIMEOUT_SECONDS = float(os.getenv("KAFKA_PUBLISH_TIMEOUT_SECONDS", "2"))
RESUME_DIR = os.getenv("RESUME_DIR", "backend/uploads/resumes")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", f"p{PAIR}_careerbridge")
SEED = os.getenv("SEED", PAIR)
CITY_SET = tuple(
    value.strip()
    for value in os.getenv(
        "CITY_SET", "San Jose,Mountain View,Palo Alto"
    ).split(",")
    if value.strip()
)

SERVICE_PORT_OFFSETS = {
    "student": 1,
    "company": 2,
    "job": 3,
    "application": 4,
    "event": 5,
    "assistant": 6,
}


def service_port(offset: int) -> int:
    """Return a deterministic local service port derived from `PORT_BASE`."""

    return PORT_BASE + offset


def domain_service_port(service_name: str) -> int:
    """Return the deterministic port for an independently runnable domain process."""

    try:
        return service_port(SERVICE_PORT_OFFSETS[service_name])
    except KeyError as exc:
        raise ValueError(f"Unsupported domain service: {service_name}") from exc
