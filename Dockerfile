# Use the smallest possible base image that can run Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY arango_compare.py .

# Set environment variables
ENV ARANGO_URL1=http://arangodb:8529
ENV ARANGO_USERNAME1=root
ENV ARANGO_PASSWORD1=testpassword
ENV ARANGO_DB_NAME1=_system

# Command to run the application
CMD ["python", "arango_compare.py"]
