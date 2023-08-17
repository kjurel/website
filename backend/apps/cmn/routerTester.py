from __future__ import annotations

from fastapi import APIRouter

testRouter = APIRouter(prefix="/test", tags=["Test"])


@testRouter.get("/")
async def test_check(name: str):
    return {"answer": f"Hello {name}"}
