FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Disable Python buffering for real-time output
ENV PYTHONUNBUFFERED=1

# Run with no privileges
USER nobody

# Default command - will be overridden by docker exec
CMD ["python"]
