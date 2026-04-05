from flask import Blueprint, request, jsonify
import jwt
import os
from functools import wraps
from db import get_connection
from mysql.connector import Error

jobs_bp = Blueprint("jobs", __name__)
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")


# ── JWT Auth Decorator ──────────────────────────────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = decoded
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


# ── POST /jobs ───────────────────────────────────────────────────────────────
@jobs_bp.route("/jobs", methods=["POST"])
@token_required
def create_job():
    data = request.get_json()

    required = ["title", "company", "location", "description", "skills_required"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO jobs (title, company, location, description, skills_required)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                data["title"].strip(),
                data["company"].strip(),
                data["location"].strip(),
                data["description"].strip(),
                data["skills_required"].strip()
            )
        )
        conn.commit()
        job_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Job posted successfully", "job_id": job_id}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500


# ── GET /jobs ────────────────────────────────────────────────────────────────
@jobs_bp.route("/jobs", methods=["GET"])
@token_required
def get_jobs():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        jobs = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert datetime to string for JSON serialization
        for job in jobs:
            if job.get("created_at"):
                job["created_at"] = str(job["created_at"])

        return jsonify({"jobs": jobs, "total": len(jobs)}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


# ── GET /match-jobs ──────────────────────────────────────────────────────────
@jobs_bp.route("/match-jobs", methods=["GET"])
@token_required
def match_jobs():
    user_id = request.user["user_id"]

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user's skills
        cursor.execute("SELECT skills FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user or not user["skills"]:
            cursor.close()
            conn.close()
            return jsonify({"error": "User skills not found"}), 404

        user_skills = [s.strip().lower() for s in user["skills"].split(",")]

        # Fetch all jobs
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        all_jobs = cursor.fetchall()
        cursor.close()
        conn.close()

        matched_jobs = []
        for job in all_jobs:
            job_skills = [s.strip().lower() for s in job["skills_required"].split(",")]
            # Check for any skill overlap
            overlap = set(user_skills) & set(job_skills)
            if overlap:
                if job.get("created_at"):
                    job["created_at"] = str(job["created_at"])
                job["matched_skills"] = list(overlap)
                matched_jobs.append(job)

        return jsonify({
            "user_skills": user_skills,
            "matched_jobs": matched_jobs,
            "total_matches": len(matched_jobs)
        }), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


# ── POST /notify ─────────────────────────────────────────────────────────────
@jobs_bp.route("/notify", methods=["POST"])
@token_required
def notify():
    data = request.get_json()
    job_id = data.get("job_id")

    if not job_id:
        return jsonify({"error": "'job_id' is required"}), 400

    user_id = request.user["user_id"]

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify job exists
        cursor.execute("SELECT id FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            cursor.close()
            conn.close()
            return jsonify({"error": "Job not found"}), 404

        # Check for duplicate notification
        cursor.execute(
            "SELECT id FROM notifications WHERE user_id = %s AND job_id = %s",
            (user_id, job_id)
        )
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            conn.close()
            return jsonify({"message": "Notification already exists for this job"}), 200

        cursor.execute(
            "INSERT INTO notifications (user_id, job_id, status) VALUES (%s, %s, %s)",
            (user_id, job_id, "sent")
        )
        conn.commit()
        notification_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Notification stored successfully",
            "notification_id": notification_id,
            "user_id": user_id,
            "job_id": job_id
        }), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500
