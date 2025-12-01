# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any are needed for your python packages)
# gcc and libpq-dev are often needed for psycopg2 or other compiled extensions
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# We copy the 'app' directory into '/app/app' because our imports are like 'from app.core...'
# and WORKDIR is /app. So if we copy ./app to ./app, the structure is preserved.
COPY app ./app

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Define environment variable for unbuffered logging
ENV PYTHONUNBUFFERED=1

# Run app.main:app when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
