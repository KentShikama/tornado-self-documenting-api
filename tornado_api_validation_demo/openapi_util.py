import json

from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin


def generate_openapi_json(handlers, file_location):
    spec = APISpec(
        title="Tornado self-documenting API validation demo",
        version="1.0.0",
        openapi_version="3.0.2",
        info=dict(description="A minimal API"),
        plugins=[TornadoPlugin(), MarshmallowPlugin()],
    )
    for handler in handlers:
        try:
            spec.path(urlspec=handler)
        except APISpecError:
            pass
    with open(file_location, "w", encoding="utf-8") as file:
        spec_dict = spec.to_dict()
        spec_dict["servers"] = []  # Swagger UI requires servers field
        json.dump(spec.to_dict(), file, indent=2)