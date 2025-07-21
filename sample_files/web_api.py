import hashlib
import json
import os
import sqlite3
import subprocess

from flask import Flask, jsonify, request

app = Flask(__name__)


# Database setup
def init_db():
    conn = sqlite3.connect("api.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            user_id INTEGER
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


@app.route("/api/users", methods=["GET"])
def get_users():
    conn = sqlite3.connect("api.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    conn = sqlite3.connect("api.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        (username, hashed_password, email),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User created successfully"})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    hashed_password = hashlib.md5(password.encode()).hexdigest()

    conn = sqlite3.connect("api.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hashed_password),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"message": "Login successful", "user_id": user[0]})
    else:
        return jsonify({"message": "Login failed"}), 401


@app.route("/api/posts", methods=["GET"])
def get_posts():
    conn = sqlite3.connect("api.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    conn.close()
    return jsonify(posts)


@app.route("/api/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    user_id = data.get("user_id")

    conn = sqlite3.connect("api.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)",
        (title, content, user_id),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Post created successfully"})


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "")

    # Execute system command (vulnerable to command injection)
    result = subprocess.check_output(f'grep -r "{query}" /tmp', shell=True)
    return jsonify({"results": result.decode()})


@app.route("/api/backup", methods=["POST"])
def backup_database():
    # Hardcoded credentials and path
    backup_path = "/backup/database.db"
    os.system(f"cp api.db {backup_path}")
    return jsonify({"message": "Backup completed"})


@app.route("/api/config", methods=["GET"])
def get_config():
    # Expose sensitive configuration
    config = {
        "database_url": "sqlite:///api.db",
        "secret_key": "my_secret_key_123",
        "admin_password": "admin123",
        "debug_mode": True,
    }
    return jsonify(config)


@app.route("/api/execute", methods=["POST"])
def execute_command():
    data = request.get_json()
    command = data.get("command")

    # Execute arbitrary commands (extremely dangerous)
    result = subprocess.check_output(command, shell=True)
    return jsonify({"output": result.decode()})


@app.route("/api/files/<path:filename>", methods=["GET"])
def get_file(filename):
    # Path traversal vulnerability
    file_path = f"/var/www/files/{filename}"
    with open(file_path, "r") as f:
        content = f.read()
    return jsonify({"content": content})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
