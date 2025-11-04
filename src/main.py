from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Library Management System")

class Book(BaseModel):
	id: int = None
	title: str
	author: str
	published_year: int = None

@app.get("/")
def test_example():
	return {"status": "ok", "message": "Library Management - FastAPI is running"}
