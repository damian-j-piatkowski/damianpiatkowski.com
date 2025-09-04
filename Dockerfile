# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Make wait-for-it.sh executable
RUN chmod +x /app/scripts/wait-for-it.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose both ports:
# - 5000 for Flask dev server
# - 8000 for Gunicorn in production
EXPOSE 5000 8000

# Environment variables (optional defaults)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# No default CMD — let docker-compose override it for dev/prod
CMD ["python", "--version"]
