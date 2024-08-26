# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl wget unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

## Install Node.js dependencies
#RUN npm install
#
## Build and minify CSS files using Gulp
#RUN npm install -g gulp-cli
#RUN gulp minifyBaseCss && gulp minifyIndexCss

# Make port 5000 (or the port specified by FLASK_RUN_PORT) available to the world outside this container
EXPOSE 5000

# Set environment variables
ENV NAME World

# Command to run the Flask app with database migration
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=${FLASK_RUN_PORT}"]
