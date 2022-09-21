FROM python:3.10

RUN pip install -U nltk
RUN python -c "import nltk; nltk.download('punkt'); nltk.data.load('tokenizers/punkt/russian.pickle')"
WORKDIR "/app"
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
