FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml ./
COPY medmentor ./medmentor
COPY webapp ./webapp
RUN pip install --no-cache-dir .
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "medmentor.bot"]
