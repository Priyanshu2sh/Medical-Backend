# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libmariadb-dev \
    default-mysql-client \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the container
COPY . .

# Expose port 8000 for Gunicorn
EXPOSE 8001

# Command to run Gunicorn as the WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "medical_books.wsgi:application"]
# CMD ["python3" "manage.py" "runserver" "0.0.0.0:8001"]