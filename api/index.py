from fastapi import FastAPI

# from .backend.core.init_app import app_factory

# from .backend.core.init_app import app_factory

app = FastAPI()
# app = FastAPI()


@app.get("/api")
def hello_world():
    return {"message": "Working!!"}


@app.get("/api/py1")
def hello_world_py1():
    return {"message": "Hello World from Python1"}


@app.get("/api/py2")
def hello_world_py2():
    return {"message": "Hello World from Python2"}


@app.get("/api/py2")
def hello_world_py3():
    return {"message": "Hello World from Python3"}


@app.get("/api/py4")
def hello_world_py4():
    return {"message": "Hello World from Python4"}


@app.get("/api/py5")
def hello_world_py5():
    return {"message": "Hello World from Python5"}


@app.get("/api/py6")
def hello_world_py6():
    return {"message": "Hello World from Python6"}


@app.get("/api/py7")
def hello_world_py7():
    return {"message": "Hello World from Python7"}


@app.get("/api/py8")
def hello_world_py8():
    return {"message": "Hello World from Python8"}


@app.get("/api/py9")
def hello_world_py9():
    return {"message": "Hello World from Python9"}


@app.get("/api/py10")
def hello_world_py10():
    return {"message": "Hello World from Python10"}


@app.get("/api/py11")
def hello_world_py11():
    return {"message": "Hello World from Python11"}


@app.get("/api/py12")
def hello_world_py12():
    return {"message": "Hello World from Python12"}


@app.get("/api/py13")
def hello_world_py13():
    return {"message": "Hello World from Python13"}


@app.get("/api/py14")
def hello_world_py14():
    return {"message": "Hello World from Python14"}


@app.get("/api/py15")
def hello_world_py15():
    return {"message": "Hello World from Python15"}


@app.get("/api/py16")
def hello_world_py16():
    return {"message": "Hello World from Python16"}


@app.get("/api/py17")
def hello_world_py17():
    return {"message": "Hello World from Python17"}
