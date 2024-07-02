# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variables
ENV ARANGO_URL1=http://localhost:8529
ENV ARANGO_USERNAME1=root
ENV ARANGO_PASSWORD1=password
ENV ARANGO_DB_NAME1=test_db1

ENV ARANGO_URL2=http://localhost:8529
ENV ARANGO_USERNAME2=root
ENV ARANGO_PASSWORD2=password
ENV ARANGO_DB_NAME2=test_db2

# Run arango_compare.py when the container launches
CMD ["python", "./arango_compare/arango_compare.py"]
