FROM python:3.9-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.9-slim

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

# Copy dependencies and application code
COPY --from=builder /root/.local /home/appuser/.local
COPY app.py .

# Update path for installed packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
