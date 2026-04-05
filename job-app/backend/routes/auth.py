from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import os
import datetime
from db import get_connection
from mysql.connector import Error

auth_bp = Blueprint("auth", __name__)
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    required = ["name", "email", "password", "skills", "location"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"'{field}' is required"}), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    skills = data["skills"].strip()
    location = data["location"].strip()
    raw_password = data["password"]

    # Hash password
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password, skills, location) VALUES (%s, %s, %s, %s, %s)",
            (name, email, hashed.decode("utf-8"), skills, location)
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

    except Error as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "Email already registered"}), 409
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate JWT token
        payload = {
            "user_id": user["id"],
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "skills": user["skills"],
                "location": user["location"]
            }
        }), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500
