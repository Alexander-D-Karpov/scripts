ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} as python


FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local
RUN mkdir "/app"
WORKDIR /app
ARG BUILD_ENVIRONMENT=local

ADD requirements.txt requirements.txt
ADD main.py main.py
ADD subscribed_chats.json subscribed_chats.json

RUN pip install -r requirements.txt

CMD ["python", "main.py"]