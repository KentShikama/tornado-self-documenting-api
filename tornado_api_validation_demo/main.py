import functools
import json
from typing import Type

import swagger_ui
import tornado.ioloop
from tornado.web import HTTPError, RequestHandler
from marshmallow import Schema, fields, ValidationError

from tornado_api_validation_demo.openapi_util import generate_openapi_json


class FooParameter(Schema):
    foo_name = fields.Str()


class FooSchema(Schema):
    output = fields.Int()


class BaseHandler(RequestHandler):
    """Application base handler"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validated_body = {}

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
                self.validated_body = schema().loads(self.request.body)
                return func(self, *args, **kwargs)
            except ValidationError as e:
                self.write_json(400, e.messages)
            except Exception as e:
                self.write_json(400, str(e))
        doc_string = f"""
        {func.__doc__}
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
        doc_string = f"""
        {func.__doc__}
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


class MainHandler(BaseHandler):
    @params(FooParameter)
    @success(FooSchema)
    async def get(self, foo_name):
        """
        Demo endpoint
        ---
        description: Foo!
        """
        if self.validated_body["foo_name"] == "Give me an error":
            raise HTTPError(404)
        elif self.validated_body["foo_name"] == "Give me another error":
            return {"Bad key": "Bad value"}
        else:
            return {"output": 5}


def make_app():
    urls = [
        (r"/([^/]+)", MainHandler),
    ]
    app = tornado.web.Application(urls)
    generate_openapi_json(handlers=urls, file_location="default.json")
    swagger_ui.tornado_api_doc(
        app,
        config_path="default.json",
        title="Tornado self-documenting API validation demo",
    )
    return app


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
