import hashlib
import json
import os
import sqlite3
from datetime import datetime


class UserManager:
    def __init__(self):
        self.db_path = "users.db"
        self.users = {}
        self.load_users()

    def load_users(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            for row in rows:
                self.users[row[0]] = {"password": row[1], "email": row[2]}
            conn.close()
        except:
            pass

    def create_user(self, username, password, email):
        if username in self.users:
            return False

        hashed_password = hashlib.md5(password.encode()).hexdigest()
        self.users[username] = {"password": hashed_password, "email": email}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (username, hashed_password, email),
        )
        conn.commit()
        conn.close()
        return True

    def authenticate(self, username, password):
        if username not in self.users:
            return False

        hashed_password = hashlib.md5(password.encode()).hexdigest()
        return self.users[username]["password"] == hashed_password

    def get_user_info(self, username):
        return self.users.get(username, {})

    def update_email(self, username, new_email):
        if username in self.users:
            self.users[username]["email"] = new_email
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET email = ? WHERE username = ?",
                (new_email, username),
            )
            conn.commit()
            conn.close()
            return True
        return False

    def delete_user(self, username):
        if username in self.users:
            del self.users[username]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True
        return False


def main():
    manager = UserManager()

    # Create some test users
    manager.create_user("admin", "admin123", "admin@example.com")
    manager.create_user("user1", "password123", "user1@example.com")

    # Test authentication
    if manager.authenticate("admin", "admin123"):
        print("Admin login successful")

    # Get user info
    user_info = manager.get_user_info("admin")
    print(f"User info: {user_info}")


if __name__ == "__main__":
    main()
