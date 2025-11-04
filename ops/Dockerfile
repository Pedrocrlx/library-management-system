FROM python:3.12

RUN pip install poetry

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create true &&\
    poetry config virtualenvs.in-project true &&\
    poetry install --no-root

COPY . .

ENV PATH="/workspace/.venv/bin:$PATH" 

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]