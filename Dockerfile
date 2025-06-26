# Dockerfile
FROM python:3.13-alpine AS base

# Copy local code to the container image.
ENV DIR_PROJECT /opt/project
ENV DIR_SRC /opt/project/src
ENV DIR_TEST /opt/project/test
RUN mkdir -p PROJECT_DIR
ENV HOME $PROJECT_DIR
WORKDIR $PROJECT_DIR

# Update pip
RUN pip install --upgrade pip


WORKDIR /app

COPY ./src/surquest/GCP/dataform-cli/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt



COPY main.py .

ENTRYPOINT ["python", "src/surquest/GCP/dataform-cli/main.py"]
