import swagger_ui
import tornado.ioloop
from tornado.web import HTTPError
from marshmallow import Schema, fields

from tornado_api_validation_demo.base_handler import BaseHandler, params, success
from tornado_api_validation_demo.openapi_util import generate_openapi_json


class FooParameter(Schema):
    foo_name = fields.Str()


class FooSchema(Schema):
    output = fields.Int()


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
