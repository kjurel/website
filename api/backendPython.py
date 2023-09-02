from fastapi import FastAPI

import backendPython

app = FastAPI(prefix="/api/python")


@app.get("/")
def hello_world1():
    return {"message": "Working!!"}
