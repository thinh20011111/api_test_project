import pytest
import os
import yaml
from config.config import load_environment_config

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="dev", 
                    help="Environment to test", 
                    choices=["lab", "dev", "staging", "production"])

@pytest.fixture(scope="session")
def env_config(request):
    env = request.config.getoption("--env")
    config = load_environment_config(env)
    config["name"] = env
    return config