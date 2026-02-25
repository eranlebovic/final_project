# 1. Base Image: Use a lightweight Python version
# Best Practice: Always pin the version (3.9-slim) to avoid breaking changes.
FROM python:3.9-slim

# Bring OS security patches (including OpenSSL/glibc) up to date
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# 2. Security: Create a non-root user
# Best Practice: Never run containers as 'root'. If hacked, they can't damage the host.
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 3. Work Directory: Set the folder inside the container
WORKDIR /app

# 4. Dependencies: Copy just the requirement file first
# Best Practice: Docker caches layers. If you change code but not requirements, 
# Docker skips this step, making builds super fast.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Application Code: Copy the rest of the app
COPY app.py .

# 6. Permissions: Give the non-root user ownership
RUN chown -R appuser:appuser /app

# 7. Execution: Switch user and start
USER appuser
EXPOSE 5000

# Best Practice: Use CMD to specify the start command
CMD ["python", "app.py"]
