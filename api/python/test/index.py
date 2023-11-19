from fastapi import FastAPI

app = FastAPI(root_path="/api/py")


@app.get("/hello")
async def hello():
    return {"message": "Hello"}
