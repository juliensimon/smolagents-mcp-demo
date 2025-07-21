import hashlib
import json
import os
import sqlite3
import subprocess
import pickle
import base64
import urllib.parse

from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'hardcoded_secret_key_123'

# Global session storage (vulnerable)
SESSIONS = {}

# Database setup
def init_db():
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/users', methods=['GET'])
def get_users():
    # No authentication required
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # Weak password hashing
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    # SQL injection vulnerability
    query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{hashed_password}', '{email}')"
    cursor.execute(query)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User created successfully'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed_password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # Insecure session management
        session_id = hashlib.md5(username.encode()).hexdigest()
        SESSIONS[session_id] = {'user_id': user[0], 'username': username}
        return jsonify({'message': 'Login successful', 'session_id': session_id})
    else:
        return jsonify({'message': 'Login failed'}), 401

@app.route('/api/posts', methods=['GET'])
def get_posts():
    # No authentication check
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    conn.close()
    return jsonify(posts)

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    user_id = data.get('user_id')
    
    # No input validation
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    # SQL injection vulnerability
    query = f"INSERT INTO posts (title, content, user_id) VALUES ('{title}', '{content}', {user_id})"
    cursor.execute(query)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Post created successfully'})

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    
    # Command injection vulnerability
    result = subprocess.check_output(f'grep -r "{query}" /tmp', shell=True)
    return jsonify({'results': result.decode()})

@app.route('/api/backup', methods=['POST'])
def backup_database():
    # Hardcoded credentials and path
    backup_path = '/backup/database.db'
    os.system(f'cp api.db {backup_path}')
    return jsonify({'message': 'Backup completed'})

@app.route('/api/config', methods=['GET'])
def get_config():
    # Expose sensitive configuration
    config = {
        'database_url': 'sqlite:///api.db',
        'secret_key': 'my_secret_key_123',
        'admin_password': 'admin123',
        'debug_mode': True,
        'database_password': 'db_password_456'
    }
    return jsonify(config)

@app.route('/api/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command')
    
    # Execute arbitrary commands (extremely dangerous)
    result = subprocess.check_output(command, shell=True)
    return jsonify({'output': result.decode()})

@app.route('/api/files/<path:filename>', methods=['GET'])
def get_file(filename):
    # Path traversal vulnerability
    file_path = f'/var/www/files/{filename}'
    with open(file_path, 'r') as f:
        content = f.read()
    return jsonify({'content': content})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # No file validation
    file = request.files['file']
    filename = file.filename
    file.save(f'/uploads/{filename}')
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    # Expose session data
    return jsonify(SESSIONS.get(session_id, {}))

@app.route('/api/admin', methods=['GET'])
def admin_panel():
    # No authentication check
    conn = sqlite3.connect('api.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'users': users,
        'posts': posts,
        'sessions': SESSIONS
    })

@app.route('/api/deserialize', methods=['POST'])
def deserialize_data():
    # Dangerous deserialization
    data = request.get_json()
    serialized_data = data.get('data')
    deserialized = pickle.loads(base64.b64decode(serialized_data))
    return jsonify({'result': str(deserialized)})

@app.route('/api/url_decode', methods=['POST'])
def url_decode():
    # URL decoding without validation
    data = request.get_json()
    url = data.get('url')
    decoded = urllib.parse.unquote(url)
    return jsonify({'decoded': decoded})

@app.route('/api/redirect', methods=['GET'])
def redirect():
    # Open redirect vulnerability
    url = request.args.get('url', '')
    return jsonify({'redirect_url': url})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    # Expose system logs
    result = subprocess.check_output('tail -n 100 /var/log/system.log', shell=True)
    return jsonify({'logs': result.decode()})

@app.route('/api/process', methods=['POST'])
def process_data():
    # XML external entity vulnerability simulation
    data = request.get_json()
    xml_data = data.get('xml')
    # Process XML without proper validation
    return jsonify({'processed': xml_data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
