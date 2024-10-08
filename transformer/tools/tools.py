from os import getenv, environ
from collections import defaultdict
import logging
import time
from functools import wraps

INPUT_PORTS: defaultdict[str, dict[str, str]] = defaultdict(dict)
OUTPUT_PORTS: defaultdict[str, dict[str, str]] = defaultdict(dict)

for k, v in environ.items():
    parts = k.split("_", maxsplit=2)
    if k.startswith("INPUT_"):
        INPUT_PORTS[parts[1]] |= {parts[2]: v}
    elif k.startswith("OUTPUT_"):
        OUTPUT_PORTS[parts[1]] |= {parts[2]: v}

def get_environment_variable(var_name: str) -> str:
    """
    Retrieve an environment variable value.
    Raise an exception if the value is not set.
    """
    value = getenv(var_name)
    if value:
        return value
    raise EnvironmentError(f"Environment variable {var_name} not set.")


def printer(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Executing {func.__name__}...")
        result = func(*args, **kwargs)
        logging.info(f"Finished executing {func.__name__}")
        logging.info("--------------------")
        return result

    return wrapper


def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise e

    return wrapper


def timer(func):
    """
    Decorator to time a function execution.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"{func.__name__} took {execution_time:.2f} seconds.")
        return result

    return wrapper
