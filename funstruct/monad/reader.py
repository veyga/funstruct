"""Reader monad — computations that read from a shared environment.

bind lets multiple computations share the same context without
passing it explicitly. Each step in the chain sees the same env.

Examples:
    >>> from funstruct.monad.reader import Reader
    >>> get_host = Reader(lambda cfg: cfg["host"])
    >>> get_port = Reader(lambda cfg: cfg["port"])
    >>> get_path = Reader(lambda cfg: cfg.get("path", "/"))
    >>> build_url = (
    ...     get_host
    ...     .bind(lambda h: get_port
    ...     .bind(lambda p: get_path
    ...     .map(lambda path: f"http://{h}:{p}{path}")))
    ... )
    >>> build_url.run({"host": "localhost", "port": 8080, "path": "/api"})
    'http://localhost:8080/api'
    >>> build_url.run({"host": "prod.co", "port": 443})
    'http://prod.co:443/'
"""

from _funstruct._reader import *  # noqa F403
