import yaml
import os

REPORTS_DIR = "reports"

def load_environment_config(env_name):
    """Tải cấu hình cho môi trường được chỉ định"""
    with open("config/environments.yaml", "r") as file:
        config = yaml.safe_load(file)
    env_config = config["environments"].get(env_name)
    if not env_config:
        raise ValueError(f"Environment '{env_name}' not found in environments.yaml")
    return env_config