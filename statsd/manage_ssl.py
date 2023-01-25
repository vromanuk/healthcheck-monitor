import os
import pathlib
from ssl import SSLContext
from typing import Any

from aiokafka.helpers import create_ssl_context


def get_ssl_context(ssl_context: dict[str, Any]) -> SSLContext:
    basedir = pathlib.Path(__file__).parent.parent
    return create_ssl_context(
        cafile=os.path.join(basedir, ssl_context["cafile"]),
        certfile=os.path.join(basedir, ssl_context["certfile"]),
        keyfile=os.path.join(basedir, ssl_context["keyfile"]),
    )
