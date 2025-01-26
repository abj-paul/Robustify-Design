# Use the official Python image as the base image
FROM python:3.10-slim

# Install system dependencies (graphviz, GCC, and build tools)
RUN apt-get update && apt-get install -y \
    #graphviz \
    libgraphviz-dev \
    gcc \
    g++ \
    make \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .
RUN apt-get update && apt-get install -y graphviz

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uvicorn fastapi pygraphviz reportlab numpy networkx scipy scikit-learn python-dotenv google-generativeai python-multipart

# Set JAVA_HOME (optional but good practice)
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Copy the rest of the application code
COPY . .

# Expose port 8000 (pipeline port)
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]