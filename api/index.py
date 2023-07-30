from fastapi import FastApi

app = FastApi()

app.get("/api-py/")
def hello():
  return {"message":"Hello from Python"}