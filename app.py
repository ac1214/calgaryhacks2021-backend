import uuid
import time
from flask import Flask, jsonify, request
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.Certificate('./firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)


@app.route('/')
def home_endpoint():
    return 'Hello World! 123'


@app.route('/create_task', methods=['POST'])
def create_task():
    # TODO: Verify?
    req_json = request.get_json()

    task_id = str(uuid.uuid4())
    doc_ref = db.collection('tasks').document(task_id)
    doc_ref.set({
        "task_id": task_id,
        "task_name": req_json["task_name"] if "task_name" in req_json else "N/A",
        "poster_id": req_json["user_id"] if "user_id" in req_json else "N/A",
        "description": req_json["description"] if "description" in req_json else "N/A",
        "volunteer_id": "N/A",
        "longitude": req_json["longitude"] if "longitude" in req_json else "N/A",
        "latitude": req_json["latitude"] if "latitude" in req_json else "N/A",
        "status": "unassigned",
        "estimated_time": req_json["estimated_time"] if "estimated_time" in req_json else "N/A",
        "reward_points": 50,
        "created": int(time.time())
    })

    return jsonify({'added': req_json}), 201


@app.route('/get_all_tasks', methods=['GET'])
def get_tasks():
    result = []
    users_ref = db.collection('tasks')
    docs = users_ref.stream()
    for doc in docs:
        result.append(doc.to_dict())

    return jsonify({'open_tasks': result}), 200


@app.route('/take_task', methods=['PUT'])
def take_task():
    # TODO: Verify?
    req_json = request.get_json()
    user_id = req_json["user_id"]
    task_id = req_json["task_id"]

    doc_ref = db.collection('tasks').document(task_id)
    doc_ref.update({
        'status': "inprogress",
        'volunteer_id': user_id
    })

    return "Successfully taken: " + task_id, 204


@app.route('/bail_on_task', methods=['PUT'])
def bail_on_task():
    # TODO: Verify?
    req_json = request.get_json()
    task_id = req_json["task_id"]

    doc_ref = db.collection('tasks').document(task_id)
    doc_ref.update({
        'status': "unassigned",
        'volunteer_id': "N/A"
    })

    return "Successfully bailed on: " + task_id, 204


@app.route('/delete_task/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    db.collection('tasks').document(task_id).delete()
    return "Successfully deleted: " + task_id, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
