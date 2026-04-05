import os
from flask import Flask
from dotenv import load_dotenv
from models import init_db
from routes.auth import auth_bp
from routes.jobs import jobs_bp

load_dotenv()

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(jobs_bp)

# Health check
@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "service": "Job Notification API"}, 200

if __name__ == "__main__":
    init_db()  # Auto-create tables on startup
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"[APP] Starting server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug)
