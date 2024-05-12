import numpy as np
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/py/test")
def main():
    return str(np.random.choice([1, 2, 3, 4, 5, 6])).encode()
