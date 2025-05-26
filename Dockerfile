# 1. Base image
FROM python:3.10

# # 2. Environment variables
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# 3. Set working directory
WORKDIR /app

# 4. Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 5. Copy all project files
COPY . /app/

# 6. Default command to run
CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]

