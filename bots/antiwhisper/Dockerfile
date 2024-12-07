FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Set environment variables (you can also set them in docker-compose or externally)
# ENV TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN

CMD ["python", "bot.py"]