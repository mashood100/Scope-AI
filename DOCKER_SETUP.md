# Docker Setup for Scope AI

This document provides instructions for running the Scope AI application using Docker.

## Prerequisites

1. Install Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Ensure Docker Desktop is running

## Running the Application

### Option 1: Using Docker Compose (Recommended)

1. **Start the entire application stack:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode (background):**
   ```bash
   docker-compose up -d --build
   ```

3. **Stop the application:**
   ```bash
   docker-compose down
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f web
   ```

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t scope-ai .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 --env-file dev.env scope-ai
   ```

## What's Included

- **Django Web Application**: Runs on port 8000
- **MongoDB Database**: Runs on port 27017 (local development only)

## Environment Variables

Make sure you have a `dev.env` file with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

## Accessing the Application

Once running, you can access:
- **Main Application**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Endpoints**: 
  - Document Search: http://localhost:8000/document-search/
  - Proposal Generator: http://localhost:8000/proposal-generator/

## Troubleshooting

1. **Port already in use**: If port 8000 is busy, modify the docker-compose.yml file to use a different port:
   ```yaml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Database connection issues**: Make sure MongoDB is running in the container and the connection string in settings.py is correct.

3. **Build issues**: Clear Docker cache:
   ```bash
   docker system prune
   docker-compose build --no-cache
   ```

## Development

For development with hot reload, the docker-compose.yml is configured to mount the current directory as a volume, so changes to your code will be reflected immediately.