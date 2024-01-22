import base64
import logging

import orjson
from google_api_service_helper import GoogleKeys

log = logging.getLogger(__name__)


def load_google_keys(v: str) -> GoogleKeys:
    try:
        json_str = base64.b64decode(v)
        data = orjson.loads(json_str)
        return GoogleKeys(**data)
    except ValueError:
        log.warning("Can not load google keys")
        raise
