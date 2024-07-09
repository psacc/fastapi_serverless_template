from fastapi import FastAPI
import os

stage = os.environ.get('STAGE', 'dev')


app = FastAPI()


@app.post("/encode/")
def index():
    return {"Hello": "World"}


@app.postget("/decode/")
def read_item():
    return {"Hello": "World"}
