from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Library Management - Minimal Example")


class Book(BaseModel):
	id: int = None
	title: str
	author: str
	published_year: int = None

@app.get("/", tags=["root"])
def read_root():
	return {"status": "ok", "message": "Library Management - FastAPI is running"}
