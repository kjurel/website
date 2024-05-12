# from fastapi import FastAPI

# from backend.controllers.codecheckr import router

from backend.init_app import App

app = App("/api/py/main").controllers({"codecheckr"}).attach_controllers().app
#
# @app.get("/api/py/main/codecheckr")
# def basic2():
#     return "workgin in basic 2"
#

# app = FastAPI()
#
#
# @app.get("/api/py/main")
# def basic():
#     return "running"
#
#
# app.include_router(router, prefix="/api/py/main")
