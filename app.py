from flask import Flask, request, jsonify, send_from_directory

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# File to store posts and admin password
DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({'posts': [], 'admin_password': 'allylsamt'}, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/posts', methods=['GET'])
def get_posts():
    data = load_data()
    return jsonify(data['posts'])

@app.route('/api/posts', methods=['POST'])
def add_post():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    data = load_data()
    if token != data['admin_password']:
        return jsonify({'message': 'Invalid token'}), 403

    new_post = request.json
    if not new_post or 'id' not in new_post or 'title' not in new_post or 'content' not in new_post or 'published' not in new_post:
        return jsonify({'message': 'Missing post data'}), 400

    # Check if post ID already exists
    if any(post['id'] == new_post['id'] for post in data['posts']):
        return jsonify({'message': 'Post with this ID already exists'}), 409

    data['posts'].insert(0, new_post) # Add to beginning
    save_data(data)
    return jsonify(new_post), 201

@app.route('/api/login', methods=['POST'])
def login():
    password = request.json.get('password')
    data = load_data()
    if password == data['admin_password']:
        return jsonify({'message': 'Login successful', 'token': data['admin_password']}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/change_password', methods=['POST'])
def change_password():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'message': 'Unauthorized'}), 401

    token = auth_header.split(' ')[1]
    data = load_data()
    if token != data['admin_password']:
        return jsonify({'message': 'Invalid token'}), 403

    new_password = request.json.get('new_password')
    if not new_password:
        return jsonify({'message': 'New password is required'}), 400

    data['admin_password'] = new_password
    save_data(data)
    return jsonify({'message': 'Password changed successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


