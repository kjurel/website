from fastapi import FastApi

app = FastApi()

app.get("/api")
def hello():
  return {"message":"Hello from Python"}