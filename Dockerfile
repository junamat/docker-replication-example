# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Esto nos evita tener que volver a descargar las dependencias de nuevo cada vez que hacemos un cambio al código.
COPY requirements.txt .

RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World
ENV THRESHOLD 9.233296204297654
ENV WINDOW_SIZE 10
ENV MODEL_NAME modelo

# Run app.py when the container launches
CMD ["python", "app.py"]
