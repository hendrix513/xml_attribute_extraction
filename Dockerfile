# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml ./
COPY main.py ./
COPY extractor.py ./
COPY sample_patent.xml ./

# Copy tests directory
COPY tests/ ./tests/

# Install dependencies using uv
RUN uv pip install --system -e .

# Set Python to unbuffered mode for better logging
ENV PYTHONUNBUFFERED=1

# Default command - run the main script with sample file
CMD ["python", "main.py", "sample_patent.xml"]
