# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

## Install Node.js dependencies
#RUN npm install
#
## Build and minify CSS files using Gulp
#RUN npm install -g gulp-cli
#RUN gulp minifyBaseCss && gulp minifyIndexCss

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0 --port=${FLASK_RUN_PORT}"]
