from pathlib import Path

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
        This endpoint is self-documenting!
        """
        if self.validated_params["foo_name"] == "Give me an error":
            raise HTTPError(404)
        elif self.validated_params["foo_name"] == "Give me another error":
            return {"Bad key": "Bad value"}
        else:
            return {"output": 5}


class NoParams(BaseHandler):
    @success(FooSchema)
    async def get(self):
        """
        No params endpoint
        """
        return {"output": 5}


class ManualWrite(BaseHandler):
    @params(FooParameter)
    async def get(self):
        """
        You can do it the old fashioned way too...
        """
        value = self.validated_params["foo_name"]
        self.set_header("Content-Type", "application/json")
        self.set_status(200)
        self.write("{'output':" + value + "}")


BASE_PATH = Path(__file__).parent
SWAGGER_PATH = str(BASE_PATH.joinpath("swagger.json"))


def make_app():
    urls = [
        (r"/noparams/?", NoParams),
        (r"/manualwrite/?", ManualWrite),
        (r"/([^/]+)", MainHandler),
    ]
    app = tornado.web.Application(urls)
    generate_openapi_json(handlers=urls, file_location=SWAGGER_PATH)
    swagger_ui.tornado_api_doc(
        app,
        config_path=SWAGGER_PATH,
        title="Tornado self-documenting API validation demo",
    )
    return app


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
