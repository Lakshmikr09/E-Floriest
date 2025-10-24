from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import re

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.farmer  # Database name
collection = db.registration  # Collection name

@app.route('/register', methods=['POST'])
def register():
    data = request.json

    # Validate required fields
    required_fields = ['firstname', 'lastname', 'dob', 'age', 'address', 'phone_number']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Validate age
    if not (0 <= data['age'] <= 120):
        return jsonify({"error": "Age must be between 0 and 120"}), 400

    # Prepare data for insertion
    user_data = {
        "firstname": data.get('firstname'),
        "lastname": data.get('lastname'),
        "dob": data.get('dob'),
        "age": data.get('age'),
        "address": data.get('address'),
        "phone_number": data.get('phone_number'),
        "username": data.get('username'),
        "password": data.get('password')  # In a real application, ensure passwords are hashed
    }
    
    # Insert data into MongoDB
    try:
        user_id = collection.insert_one(user_data).inserted_id
        return jsonify({"message": "Registration successful", "user_id": str(user_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json

    # Validate required fields
    if 'username' not in data or 'password' not in data:
        return jsonify({"error": "Username and password are required"}), 400

    # Fetch user from the database
    user = collection.find_one({"username": data['username'], "password": data['password']})
    
    if user:
        return jsonify({"message": "Login successful", "user_id": str(user['_id'])}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/users', methods=['GET'])
def get_users():
    users = list(collection.find())
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
    return jsonify(users), 200

if __name__ == '__main__':
    app.run(debug=True)
