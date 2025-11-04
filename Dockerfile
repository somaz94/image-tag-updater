# 🏗 Stage 1: Build dependencies
FROM python:3.14-slim AS builder

# Set working directory
WORKDIR /usr/src

# Copy only necessary files (avoid copying unnecessary files like .git, backup, tests, etc.)
COPY main.py .
COPY src/ ./src/
COPY requirements.txt .

# 🏗 Final Stage: Minimal runtime image
FROM python:3.14-slim

# Install only necessary system utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src

# Copy only necessary files from builder
COPY --from=builder /usr/src/main.py /usr/src/main.py
COPY --from=builder /usr/src/src /usr/src/src
COPY --from=builder /usr/src/requirements.txt /usr/src/requirements.txt

# Install Python dependencies (if any)
RUN pip install --no-cache-dir -r requirements.txt

# Configure the container to be run as an executable
ENTRYPOINT ["python", "/usr/src/main.py"]