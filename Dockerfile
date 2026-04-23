# Use Red Hat Universal Base Image (UBI) - no rate limits in OpenShift
FROM registry.access.redhat.com/ubi9/python-311:latest

# Switch to root for installations
USER 0

WORKDIR /app

# Install system dependencies if needed
RUN dnf install -y gcc && dnf clean all

# Copy requirements and install Python dependencies
COPY config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .

# Set permissions for OpenShift (UBI already has user 1001)
RUN chown -R 1001:0 /app && \
    chmod -R g=u /app

# Switch to non-root user (already exists in UBI)
USER 1001

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]