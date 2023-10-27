# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /app/

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application
CMD ["python", "app.py"]
