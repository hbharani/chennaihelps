import uvicorn
import os

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    # The original Flask app used "192.168.0.3" and Flask's default port 5000.
    # Uvicorn defaults to "127.0.0.1" and port 8000.
    # We'll use the original host and a common port like 8000.
    # Debug mode in Flask is similar to --reload in Uvicorn.
    host = os.getenv("APP_HOST", "192.168.0.3")
    port = int(os.getenv("APP_PORT", "8000"))
    
    print(f"Starting Uvicorn server on {host}:{port}")
    
    uvicorn.run("main:app", host=host, port=port, reload=True)
