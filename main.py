import os
from typing import Union
from fastapi import FastAPI
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key=os.getenv("OPEN_AI_KEY")
openai.organization=os.getenv("OPEN_AI_ORG")

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
