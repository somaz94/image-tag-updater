FROM python:3.14-slim

# Install necessary packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src

# Copy application source
COPY main.py .
COPY src/ src/
COPY requirements.txt .

# Install Python dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Configure the container to be run as an executable
ENTRYPOINT ["python", "/usr/src/main.py"]