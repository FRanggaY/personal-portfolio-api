# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /code

# copy
COPY . .

# Copy the requirements file and install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run your FastAPI app (for live server)
# get variable port from environment variables, default to 5002 if not set
CMD uvicorn --host 0.0.0.0 --port ${PORT:-5002} app.main:app