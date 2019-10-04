FROM python:3
RUN pip install pipenv
ADD . /app
WORKDIR /app
RUN pipenv install --system
CMD ["python3", "main.py"]