# Tornado Self-Documenting API with Request/Response Validation Demo

## Running

1. `pipenv install`
2. `PYTHONPATH=. pipenv run python tornado_api_validation_demo/main.py`

## Basic "Library" Use

```python
from tornado.web import HTTPError
from marshmallow import Schema, fields

from tornado_api_validation_demo.base_handler import BaseHandler, params, success

class FooParameter(Schema):
    foo_name = fields.Str()
    
class FooSchema(Schema):
    output = fields.Int()

class MainHandler(BaseHandler):
    @params(FooParameter)
    @success(FooSchema)
    async def get(self):
        """
        This endpoint is self-documenting!
        """
        if self.validated_params["foo_name"] == "Give me an error":
            raise HTTPError(404)
        else:
            return {"output": 5}
```

Validated parameters are injected into `self.validated_params` (you can 
still use `self.request.body` for unvalidated body/parameters). The return 
value is validated and serialized into json output.

## OpenAPI spec generation

The OpenAPI spec is automatically generated on run.

See https://gist.github.com/KentShikama/7a75ac91d7c5387b2002d30c3e66cee8 for 
generated OpenAPI spec. Paste link into http://api.openapi-generator.tech/index.html or a different OpenAPI 
generator to view spec in HTML.

## References

- Starting point was https://github.com/juhoen/tornado-swagger-example
