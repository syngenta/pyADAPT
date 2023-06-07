"""pyadapt.schemas - JSON Schema validation utilities.

Author: Lucas Rezac <lucas.rezac@syngenta.com>
"""

import json
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, TypeVar, Union, cast
from uuid import UUID

import jsonschema
from jsonschema import FormatChecker
from jsonschema import ValidationError as ValidationError
from jsonschema.validators import RefResolver
from typing_extensions import ParamSpec

__all__ = [
    "JSONPrimitive",
    "JSONObject",
    "JSONArray",
    "JSONValue",
    "check_uuid",
    "check_uuid_uuid",
    "validate",
    "validate_result",
    "get_schema",
]

JSONPrimitive = Union[None, bool, int, float, str]
JSONObject = Dict[str, "JSONValue"]
JSONArray = List["JSONValue"]
JSONValue = Union[JSONPrimitive, JSONObject, JSONArray]

_R = TypeVar("_R", bound=JSONValue)
_P = ParamSpec("_P")

resolver = RefResolver(
    base_uri=f"{Path(__file__).parent.as_uri()}/", referrer=cast(Any, True)
)
format_checker = FormatChecker()


@format_checker.checks("uuid", raises=(ValueError, TypeError))
def check_uuid(value: object) -> bool:
    if not isinstance(value, str):
        raise TypeError("uuids must be strings")
    UUID(value)
    return True


@format_checker.checks("uuid_uuid", raises=(ValueError, TypeError))
def check_uuid_uuid(value: object) -> bool:
    if not isinstance(value, str):
        raise TypeError("uuids must be strings")
    first, second = value.split("_", 1)
    UUID(first)
    UUID(second)
    return True


def validate(value: JSONValue, schema: str):
    jsonschema.validate(
        instance=value,
        schema=get_schema(schema),
        resolver=resolver,
        format_checker=format_checker,
    )


def validate_result(schema: Union[str, JSONObject]):
    """`validate_result("schema")` is a decorator that expects its decorated functions' return values to match
    the given schema `"schema"` obtained via `get_schema`.

    Example:
    >>> @validate_result("Asset")
    def get_asset(...) -> ...: ...

    will require the return value of `get_asset` to validate `pyadapt/schemas/Asset.schema.json`."""
    schema = get_schema(schema)

    def decorator(func: Callable[_P, _R], /) -> Callable[_P, _R]:
        @wraps(func)
        def decorated(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            result = func(*args, **kwargs)
            jsonschema.validate(
                instance=result,
                schema=schema,
                resolver=resolver,
                format_checker=format_checker,
            )
            return result

        return decorated

    return decorator


def get_schema(schema: Union[str, JSONObject]) -> JSONObject:
    """Gets a schema from the `pyadapt/schemas` directory
    with the given name. E.g. `"Operation"` -> load file `syngenta_databus_shared/json_schemas/Operation.schema.json`.

    You can also pass in a raw schema object which will be returned unchanged."""
    if isinstance(schema, str):
        return _get_schema_from_file(schema)
    elif isinstance(schema, dict):
        return schema
    else:
        raise TypeError("'schema' must be a schema name or a schema object")


@lru_cache
def _get_schema_from_file(schema_name: str) -> JSONObject:
    if not schema_name.endswith(".schema.json"):
        if schema_name.endswith(".json"):
            schema_name = f"{schema_name[:-5]}.schema.json"
        else:
            schema_name += ".schema.json"
    with (Path(__file__).parent / schema_name).open("r") as file:
        return json.load(file)
