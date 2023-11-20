from fastapi import FastAPI

app = FastAPI()


@app.get("/api/py/test")
async def hello():
    return {"message": "Hello"}


app
