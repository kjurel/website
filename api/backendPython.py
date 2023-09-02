from fastapi import FastAPI

import backendPython

app = FastAPI(root_path="/api/python")


@app.get("/")
def hello_world1():
    return {"message": "Working!!"}
