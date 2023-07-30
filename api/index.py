from fastapi import FastAPI

app = FastAPI()

@app.get("/api")
def hello_world():
    return {"message": "Hello World"}


@app.get("/api/py")
def hello_world():
    return {"message": "Hello World from Python"}