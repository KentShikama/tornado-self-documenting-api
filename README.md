# Tornado Self-Documenting API with Request/Response Validation Demo

## Running

1. `pipenv install`
2. `PYTHONPATH=. pipenv run python tornado_api_validation_demo/main.py`
3. Navigate to http://localhost:8888/api/doc to see generated documentation

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

## References

- Starting point was https://github.com/juhoen/tornado-swagger-example
