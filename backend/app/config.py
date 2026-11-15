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


def service_port(offset: int) -> int:
    """Return a deterministic local service port derived from `PORT_BASE`."""

    return PORT_BASE + offset
