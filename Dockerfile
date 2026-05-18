FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy over orchestrator workspace files
COPY . .

EXPOSE 8000

# Fire up production backend server
CMD ["uvicorn", "server.py:app", "--host", "0.0.0.0", "--port", "8000"]
