from __future__ import annotations

from celery.result import AsyncResult
from fastapi import APIRouter

workerRouter = APIRouter(prefix="/task", tags=["Worker Tasks"])


@workerRouter.get("/")
async def tasks_check(task_id: str):
  task_result = AsyncResult(task_id)
  result = {
      "task_id": task_id,
      "task_info": task_result.info,
      "task_status": task_result.state,
      "task_result": task_result.result,
  }
  return result
