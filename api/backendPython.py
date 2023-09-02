from fastapi import FastAPI

import backendPython

app = FastAPI(docs_url="/api/python/docs", openapi_url="/api/python/openapi.json")


@app.get("/api/python")
def hello_world1():
    return {"message": "Working!!"}
