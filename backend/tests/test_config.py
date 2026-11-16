from backend.app import config


def test_pair09_defaults_preserve_required_derived_values():
    assert config.PAIR == "09"
    assert config.PORT_BASE == 9090
    assert config.RESOURCE_PREFIX == "p09"
    assert config.KAFKA_PREFIX == "p09"
    assert config.SEED == "09"
    assert config.CITY_SET == ("San Jose", "Mountain View", "Palo Alto")
    assert config.service_port(0) == 9090
    assert config.service_port(1) == 9091


def test_resume_storage_path_is_environment_configurable():
    assert config.RESUME_DIR
    assert config.RESUME_DIR.replace("\\", "/").endswith("backend/uploads/resumes")
