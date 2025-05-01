FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=sqllabs.settings
ENV PORT=8000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create an empty directory for static files
RUN mkdir -p /app/staticfiles

# Run collectstatic
RUN python manage.py collectstatic --noinput

# Create a non-root user to run the container
RUN addgroup --system django && adduser --system --group django
RUN chown -R django:django /app
USER django

# Create example exercises
RUN python create_all_exercises.py

# Expose the port
EXPOSE $PORT

# Start gunicorn
CMD gunicorn sqllabs.wsgi:application --bind 0.0.0.0:$PORT
