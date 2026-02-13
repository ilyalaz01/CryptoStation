# 1. Use the lightweight Python 3.10 image
FROM python:3.10-slim

# 2. Install system libraries (needed for psutil and postgres)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Create the working directory
WORKDIR /app

# 4. Copy the list of libraries and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy all our code inside the container
COPY . .

# 6. Startup command
CMD ["python", "-m", "app.main"]
