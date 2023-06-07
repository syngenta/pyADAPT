#!python3
from functools import partial, wraps
from operator import itemgetter
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union, cast

from typing_extensions import ParamSpec, TypeGuard

from pyadapt.schemas import JSONValue

_R = TypeVar("_R")
_P = ParamSpec("_P")
_T = TypeVar("_T")

sort_order = (
    "$id",
    "$schema",
    "$ref",
    "$comment",
    "title",
    "description",
    "type",
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "maxLength",
    "minLength",
    "pattern",
    "format",
    "contentMediaType",
    "contentEncoding",
    "items",
    "additionalItems",
    "maxItems",
    "minItems",
    "uniqueItems",
    "contains",
    "properties",
    "patternProperties",
    "additionalProperties",
    "propertyNames",
    "required",
    "dependencies",
    "maxProperties",
    "minProperties",
    "const",
    "enum",
    "if",
    "then",
    "else",
    "allOf",
    "anyOf",
    "oneOf",
    "not",
    "default",
    "examples",
    "definitions",
)


def trycatch(
    func: Callable[_P, _R], /, default: _R, raises: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
) -> Callable[_P, _R]:
    @wraps(func)
    def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, raises):
                return default
            raise

    return wrapped


def islistof(value: Any, /, elemtype: Type[_T]) -> TypeGuard[List[_T]]:
    return isinstance(value, list) and all(isinstance(elem, elemtype) for elem in value)


def sort_schema(schema: JSONValue, /) -> JSONValue:
    if not isinstance(schema, dict):
        return schema
    result = {}
    for key in sorted(schema.keys(), key=trycatch(sort_order.index, default=-1, raises=ValueError)):
        value = schema[key]
        sorter = sorters.get(key)
        if sorter is not None:
            value = sorter(value)
        result[key] = value
    return result


def sort_schema_array(schemas: JSONValue, /) -> JSONValue:
    if not isinstance(schemas, list):
        return schemas
    return list(map(sort_schema, schemas))


def sort_schema_array_or_schema(schema_or_schemas: JSONValue, /) -> JSONValue:
    if isinstance(schema_or_schemas, dict):
        return sort_schema(schema_or_schemas)
    if isinstance(schema_or_schemas, list):
        return sort_schema_array(schema_or_schemas)
    return schema_or_schemas


def sort_string_list(strings: JSONValue, /) -> JSONValue:
    if not islistof(strings, str):
        return strings
    return cast(JSONValue, sorted(strings))


def sort_dict(d: JSONValue, /, sort_value: Optional[Callable[[JSONValue], JSONValue]] = None) -> JSONValue:
    if not isinstance(d, dict):
        return d
    sorted_items = sorted(d.items(), key=itemgetter(0))
    if sort_value is not None:
        sorted_items = [(key, sort_value(value)) for key, value in sorted_items]
    return dict(sorted_items)


def sort_dict_of_schemas(d: JSONValue, /) -> JSONValue:
    return sort_dict(d, sort_value=sort_schema)


def sort_string_list_or_schema(strings_or_schema: JSONValue, /) -> JSONValue:
    if isinstance(strings_or_schema, dict):
        return sort_schema(strings_or_schema)
    if isinstance(strings_or_schema, list):
        return sort_string_list(strings_or_schema)
    return strings_or_schema


type_sort_order = ("null", "boolean", "integer", "number", "string", "array", "object")


def sort_type(types: JSONValue, /) -> JSONValue:
    if not islistof(types, str):
        return types
    return cast(JSONValue, sorted(types, key=trycatch(type_sort_order.index, default=-1, raises=ValueError)))


sorters: Dict[str, Callable[[JSONValue], JSONValue]] = {
    "type": sort_type,
    "items": sort_schema_array_or_schema,
    "additionalItems": sort_schema,
    "contains": sort_schema,
    "properties": sort_dict_of_schemas,
    "patternProperties": sort_dict_of_schemas,
    "additionalProperties": sort_schema,
    "propertyNames": sort_schema,
    "required": sort_string_list,
    "dependencies": partial(sort_dict, sort_value=sort_string_list_or_schema),
    "enum": sort_string_list,
    "if": sort_schema,
    "then": sort_schema,
    "else": sort_schema,
    "allOf": sort_schema_array,
    "anyOf": sort_schema_array,
    "oneOf": sort_schema_array,
    "not": sort_schema,
    "definitions": sort_dict_of_schemas,
}


def main(argv: Optional[List[str]] = None):
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=Path, default=Path("."), nargs="+")
    args = parser.parse_args(argv)
    files: Set[Path] = set(args.files)

    def process(path: Path):
        try:
            with path.open("r") as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise Exception(f"error occurred while parsing {path}") from e
        data = sort_schema(data)
        with path.open("w") as file:
            json.dump(data, file, indent=2)

    for filepath in files:
        if filepath.is_dir():
            for path in filepath.glob("*.schema.json"):
                process(path)
        else:
            process(filepath)


if __name__ == "__main__":
    main()
