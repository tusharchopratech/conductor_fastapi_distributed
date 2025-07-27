FROM python:3.13-slim

WORKDIR /app

RUN pip3 install poetry
# RUN pip3 install uvicorn
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-root
COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "src/main.py"]