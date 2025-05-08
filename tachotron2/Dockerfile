# Use the official Python image with a compatible version
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app/

# Expose the port your application runs on
EXPOSE 50051

# Define the command to run your application
CMD ["python", "server.py"]
