ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION} as python


FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local
RUN mkdir "/app"
WORKDIR /app
ARG BUILD_ENVIRONMENT=local
RUN apt-get update && apt-get install -y ffmpeg && \
    apt-get purge -y --auto-remove -o APT:AutoRemove:RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/*

ADD requirements.txt requirements.txt
ADD main.py main.py

RUN pip install -r requirements.txt

CMD ["python", "main.py"]