from fastapi import FastAPI

from backend.core.init_app import app_factory

# app = app_factory()
app = FastAPI()


@app.get("/api")
def hello_world1():
    return {"message": "Working!!"}


# @app.get("/api/py")
# def hello_world():
#     return {"message": "Hello World from Python"}
