FROM python:3.10

WORKDIR "/app"
COPY . .
RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
