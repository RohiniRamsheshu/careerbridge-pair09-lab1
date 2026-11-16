from backend.app import config
from backend.app.service_entrypoint import SERVICE_PREFIXES, create_service_app


def test_domain_service_ports_are_pair_base_derived():
    assert config.domain_service_port("student") == 9091
    assert config.domain_service_port("assistant") == 9096


def test_each_domain_boundary_has_health_and_owned_route():
    for service_name, prefixes in SERVICE_PREFIXES.items():
        service_app = create_service_app(service_name)
        routes = {route.path for route in service_app.routes}
        assert "/health" in routes
        assert "/service-info" in routes
        assert prefixes
