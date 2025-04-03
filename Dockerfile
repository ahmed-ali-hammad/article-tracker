FROM python:3.13

RUN apt update && apt install -y postgresql

WORKDIR /code

RUN pip install --upgrade pip && pip install pipenv 

ENV PIPENV_CUSTOM_VENV_NAME="article-tracker"

# COPY ./Pipfile /code/Pipfile
# COPY ./Pipfile.lock /code/Pipfile.lock
# RUN pipenv install --dev