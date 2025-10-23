from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Replace 'your_mongodb_uri' with your actual MongoDB URI
app.config["MONGO_URI"] = "mongodb://localhost:27017/farmer"
mongo = PyMongo(app)

# Collections
activities_collection = mongo.db.activities
sales_collection = mongo.db.sales
orders_collection = mongo.db.orders
owner_collection = mongo.db.owner

@app.route('/api/add-activity', methods=['POST'])
def add_activity():
    # Get data from the request
    data = request.json
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    # Validate required fields
    required_fields = ['farmerName', 'age', 'kgs', 'totalAmount', 'rate', 'flowerName', 'cash', 'date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Prepare data for insertion
    activity_data = {
        "farmerName": data.get('farmerName'),
        "age": data.get('age'),
        "kgs": data.get('kgs'),
        "totalAmount": data.get('totalAmount'),
        "rate": data.get('rate'),
        "flowerName": data.get('flowerName'),
        "cash": data.get('cash'),
        "date": data.get('date')
    }

    # Insert activity data into MongoDB
    result = activities_collection.insert_one(activity_data)
    if result.inserted_id:
        # Convert ObjectId to string
        activity_data['_id'] = str(result.inserted_id)
        return jsonify({'message': 'Activity added successfully', 'activity': activity_data}), 201
    else:
        return jsonify({'error': 'Failed to add activity'}), 500

@app.route('/api/get-activities', methods=['GET'])
def get_activities():
    activities = list(activities_collection.find())
    for activity in activities:
        activity['_id'] = str(activity['_id'])  # Convert ObjectId to string
    return jsonify(activities), 200

@app.route('/api/total_sales', methods=['GET', 'POST'])
def total_sales():
    if request.method == 'GET':
        sales = sales_collection.find_one()
        return jsonify(sales)
    elif request.method == 'POST':
        new_total_sales = request.json.get('total_sales')
        sales_collection.update_one({}, {"$set": {"total_sales": new_total_sales}}, upsert=True)
        return jsonify({"message": "Total sales updated successfully"}), 200

@app.route('/api/recent_orders', methods=['GET', 'POST'])
def recent_orders():
    if request.method == 'GET':
        orders = orders_collection.find()
        return dumps(orders)
    elif request.method == 'POST':
        new_order = request.json.get('order')
        orders_collection.insert_one({"order": new_order})
        return jsonify({"message": "Order added successfully"}), 201

@app.route('/api/owner_details', methods=['GET', 'POST'])
def owner_details():
    if request.method == 'GET':
        details = owner_collection.find_one()
        return jsonify(details)
    elif request.method == 'POST':
        owner_details = {
            "name": request.json.get('name'),
            "experience": request.json.get('experience'),
            "location": request.json.get('location'),
            "specialty": request.json.get('specialty')
        }
        owner_collection.update_one({}, {"$set": owner_details}, upsert=True)
        return jsonify({"message": "Owner details updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
