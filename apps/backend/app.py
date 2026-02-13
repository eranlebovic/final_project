from flask import Flask, jsonify
from flask_cors import CORS
import os
import redis  # Import the Redis library

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION (The 12-Factor Way) ---
# We read these from Kubernetes Environment Variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Initialize Redis Connection
# We use a try/except block so the app doesn't crash if Redis is down
try:
    r = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        password=REDIS_PASSWORD, 
        decode_responses=True # Returns strings instead of bytes
    )
    r.ping() # Test connection
    redis_alive = True
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_alive = False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "backend-api",
        "database_connected": redis_alive
    }), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "message": "Hello from the Python Backend!",
        "pod_name": os.getenv("HOSTNAME", "local-dev"),
        "secret_code": 12345
    }), 200

# --- NEW ENDPOINT: The Database Hit ---
@app.route('/api/counter', methods=['GET'])
def get_counter():
    if not redis_alive:
        return jsonify({"error": "Database unavailable"}), 503
    
    # Increment a counter in Redis atomically
    count = r.incr('api_hit_count')
    
    return jsonify({
        "message": "Database request successful",
        "total_hits": count,
        "served_by": os.getenv("HOSTNAME")
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
