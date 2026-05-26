import logging
import time
from dataclasses import dataclass, field
from functools import wraps

import requests

logger = logging.getLogger("atenciones.integrations")


@dataclass
class CircuitState:
    failure_count: int = 0
    open_until: float = 0.0
    threshold: int = 5
    recovery_timeout: float = 60.0


def circuit_breaker(state: CircuitState):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if time.time() < state.open_until:
                raise requests.RequestException("Circuit breaker abierto")
            try:
                result = func(*args, **kwargs)
                state.failure_count = 0
                return result
            except requests.RequestException:
                state.failure_count += 1
                if state.failure_count >= state.threshold:
                    state.open_until = time.time() + state.recovery_timeout
                raise

        return wrapper

    return decorator


class BaseIntegrationClient:
    timeout: int = 5

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.circuit = CircuitState()

    def _get(self, path: str) -> dict:
        @circuit_breaker(self.circuit)
        def _request():
            url = f"{self.base_url}{path}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        return _request()
