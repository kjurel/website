from fastapi import APIRouter
from fastapi_class import View


@View(testRouter := APIRouter(prefix="/test", tags=["Testing"]))
class TestView:
    def get(self, name: str):
        return {"answer": f"Hello {name}"}
