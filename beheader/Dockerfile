FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for beheader (ffmpeg, imagemagick, etc.)
# This is a placeholder, actual installation might be more complex
RUN apt-get update && apt-get install -y ffmpeg imagemagick

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]