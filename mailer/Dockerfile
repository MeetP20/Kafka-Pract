# Use the slim variant of Python to reduce image size
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1

# Run the Kafka mailer service
CMD ["python", "mailer.py"]
