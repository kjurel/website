from fastapi import FastAPI

import backendPython

app = FastAPI()


@app.get("/api/python")
def hello_world1():
    return {"message": "Working!!"}
