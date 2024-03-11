FROM python:3.12

WORKDIR /code

COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry install

COPY . ./

ENV SECRET_KEY="generate_a_new_strong_secret_key"
ENV DEBUG=True

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]