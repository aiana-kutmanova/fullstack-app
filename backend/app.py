from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import os
import time

app = Flask(__name__)
CORS(app)

def get_db():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

def wait_for_db(max_retries=30):
    """Wait for database to be ready before initializing"""
    for i in range(max_retries):
        try:
            conn = get_db()
            conn.close()
            print("✓ Database is ready!")
            return True
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries}: Waiting for database... {str(e)}")
            if i < max_retries - 1:
                time.sleep(2)
    print("✗ Could not connect to database after retries")
    return False

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT id, text, created_at FROM items ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{'id': r[0], 'text': r[1], 'created_at': str(r[2])} for r in rows])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data', methods=['POST'])
def add_data():
    body = request.json
    text = body.get('text', '')
    if not text:
        return jsonify({'error': 'text required'}), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO items (text) VALUES (%s) RETURNING id, created_at', (text,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': row[0], 'text': text, 'created_at': str(row[1])}), 201

@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM items WHERE id = %s', (item_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'deleted': item_id})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Wait for database to be ready
    if wait_for_db():
        init_db()
        print("✓ Database initialized successfully")
    else:
        print("✗ Failed to initialize database")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)