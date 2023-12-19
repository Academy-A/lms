from functools import partial

import orjson
from aiohttp import ClientSession
from aiohttp.web_response import json_response
from pyparsing import Any


def dumps(*args: Any, **kwargs: Any) -> str:
    return orjson.dumps(*args, **kwargs).decode()


fast_json_response = partial(json_response, dumps=dumps)


def create_web_session(raise_for_status: bool = False) -> ClientSession:
    return ClientSession(
        raise_for_status=raise_for_status,
        json_serialize=dumps,
    )
