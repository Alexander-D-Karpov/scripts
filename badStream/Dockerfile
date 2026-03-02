FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir aiohttp Pillow python-dotenv

WORKDIR /app
COPY bad_stream.py .
COPY bad_apple.mp4 .

CMD ["python3", "bad_stream.py"]