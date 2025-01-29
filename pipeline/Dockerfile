# Use the official Python image as the base image
FROM python:3.10-slim

# Install system dependencies including Java
RUN apt-get update && apt-get install -y \
    libgraphviz-dev \
    gcc \
    g++ \
    make \
    cmake \
    graphviz \
    default-jdk \  
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies --no-cache-dir 
RUN pip install -r requirements.txt
RUN pip install uvicorn fastapi pygraphviz reportlab numpy networkx scipy scikit-learn python-dotenv google-generativeai python-multipart

# Set JAVA_HOME (adjusted for default-jdk path)
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="$JAVA_HOME/bin:${PATH}"

# Copy the rest of the application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]