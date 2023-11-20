import os
import typing as t
from importlib import import_module

import uvicorn
from fastapi import FastAPI

from .utils.schemas import File


def find_py_files(directory: str) -> t.Generator[File, None, None]:
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path: str = os.path.join(root, file)
                file_name: str = os.path.splitext(file)[0]
                import_string: str = file_path.replace(os.sep, ".")[:-3]
                import_string = (
                    import_string[import_string.find("api") :]
                    if "api" in import_string
                    else import_string
                )

                yield File(name=file_name, path=file_path, import_string=import_string)


def dev():
    app = FastAPI()

    api_path = os.path.abspath(__file__).replace("backend/run.py", "api/")
    for f in find_py_files(api_path):
        mod = import_module(f.import_string)
        try:
            mapp = mod.__getattr__("app")
        except AttributeError as E:
            continue
        app.mount("/", mapp)

    uvicorn.run(app)
