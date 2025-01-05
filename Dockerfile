FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY certification_service ./certification_service
RUN pip install --no-cache-dir .

COPY . .

ENV PYTHONPATH=/app
ENV FLASK_APP=certification_service/app.py
ENV FLASK_ENV=development

EXPOSE 8080

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
