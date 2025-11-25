FROM python:3.12

RUN pip install poetry

WORKDIR /app

COPY .env /app/

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create true &&\
    poetry config virtualenvs.in-project false &&\
    poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "django-app/manage.py", "runserver", "0.0.0.0:8000"]