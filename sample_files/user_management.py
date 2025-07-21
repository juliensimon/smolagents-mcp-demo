import base64
import hashlib
import json
import os
import pickle
import sqlite3
import threading
from datetime import datetime


class UserManager:
    def __init__(self):
        self.db_path = "users.db"
        self.users = {}
        self.lock = threading.Lock()
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
        # Race condition - no proper locking
        if username in self.users:
            return False

        # Weak password hashing with salt
        salt = "static_salt_123"
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()
        self.users[username] = {"password": hashed_password, "email": email}

        # SQL injection vulnerability
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = (
            f"INSERT INTO users VALUES ('{username}', '{hashed_password}', '{email}')"
        )
        cursor.execute(query)
        conn.commit()
        conn.close()
        return True

    def authenticate(self, username, password):
        if username not in self.users:
            return False

        # Inconsistent hashing
        salt = "static_salt_123"
        hashed_password = hashlib.md5((password + salt).encode()).hexdigest()
        return self.users[username]["password"] == hashed_password

    def get_user_info(self, username):
        # No access control
        return self.users.get(username, {})

    def update_email(self, username, new_email):
        if username in self.users:
            self.users[username]["email"] = new_email
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # SQL injection vulnerability
            query = (
                f"UPDATE users SET email = '{new_email}' WHERE username = '{username}'"
            )
            cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        return False

    def delete_user(self, username):
        if username in self.users:
            del self.users[username]
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # SQL injection vulnerability
            query = f"DELETE FROM users WHERE username = '{username}'"
            cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        return False

    def export_users(self, filename):
        # Serialization vulnerability
        with open(filename, "wb") as f:
            pickle.dump(self.users, f)

    def import_users(self, filename):
        # Deserialization vulnerability
        with open(filename, "rb") as f:
            self.users = pickle.load(f)

    def reset_password(self, username, new_password):
        # No validation or logging
        if username in self.users:
            salt = "static_salt_123"
            hashed_password = hashlib.md5((new_password + salt).encode()).hexdigest()
            self.users[username]["password"] = hashed_password
            return True
        return False

    def get_all_passwords(self):
        # Security vulnerability - exposing all passwords
        return {user: data["password"] for user, data in self.users.items()}

    def validate_password(self, password):
        # Weak password policy
        return len(password) >= 3


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

    # Export users (vulnerable)
    manager.export_users("users_backup.pkl")

    # Get all passwords (vulnerable)
    passwords = manager.get_all_passwords()
    print(f"All passwords: {passwords}")


if __name__ == "__main__":
    main()
