import functools
import json
from typing import Type

from tornado.web import RequestHandler
from marshmallow import Schema, ValidationError


class BaseHandler(RequestHandler):
    """Application base handler"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_params = {}

    def write_json(self, status, data):
        self.set_header("Content-Type", "application/json")
        self.set_status(status)
        self.write(json.dumps(data, default=str))
        self.finish()


def params(schema: Type[Schema]):
    def decorator(func):
        @functools.wraps(func)
        def add_validation_and_doc(self, *args, **kwargs):
            try:
                self.validated_params = schema().loads(self.request.body)
                return func(self, *args, **kwargs)
            except ValidationError as e:
                self.write_json(400, e.messages)
            except Exception as e:
                self.write_json(400, str(e))
        separator = "" if "---" in func.__doc__ else "---"
        doc_string = f"""
        {func.__doc__}
        {separator}
        requestBody:
            description: {schema.__doc__}
            required: True
            content:
                application/json:
                    schema:
                        {schema.__name__}
        """
        add_validation_and_doc.__doc__ = doc_string
        return add_validation_and_doc
    return decorator


def success(schema: Type[Schema]):
    def decorator(func):
        @functools.wraps(func)
        async def add_response_and_doc(self, *args, **kwargs):
            result = await func(self, *args, **kwargs)
            errors = schema().validate(result)
            if errors:
                self.write_json(400, errors)
            else:
                self.write_json(200, result)
        separator = "" if "---" in func.__doc__ else "---"
        doc_string = f"""
        {func.__doc__}
        {separator}
        responses:
            200:
                description: {schema.__doc__}
                content:
                    application/json:
                        schema:
                            {schema.__name__}
        """
        add_response_and_doc.__doc__ = doc_string
        return add_response_and_doc
    return decorator