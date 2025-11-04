FROM python 3.12

WORKDIR /app

RUN pip install poetry

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "uvicorn", "src.main:app", "--host", "--reload", "--port", "8000"]