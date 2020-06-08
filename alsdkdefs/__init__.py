import os
import glob


def get_apis_dir():
    return f"{os.path.dirname(__file__)}/apis"


def list_services():
    base_dir = get_apis_dir()
    return sorted(next(os.walk(base_dir))[1])


def get_service_defs(service_name):
    service_dir = "/".join([get_apis_dir(), service_name])
    return glob.glob(f"{service_dir}/{service_name}.v*.yaml")