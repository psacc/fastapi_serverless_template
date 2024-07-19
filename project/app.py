from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from mangum import Mangum

from project import router

app = FastAPI()
app.include_router(router.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Project",
        version="1.0.0",
        openapi_version="3.0.2",
        summary="Project APIs",
        description="Project APIs",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

handler = Mangum(app)
