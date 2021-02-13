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


@app.route('/get_problems', methods=['GET'])
def get_problems():
    if 'user_id' not in request.args or 'session_id' not in request.args:
        return jsonify({}), 500

    requester_user_id = request.args['user_id']
    session_id = request.args['session_id']

    # get session
    session = db.collection('sessions').document(session_id).get().to_dict()

    requester_problem_ids = []
    partner_problem_ids = []

    if requester_user_id == session['user_one']:
        requester_problem_ids = session['user_one_questions']
        partner_problem_ids = session['user_two_questions']
        
    elif requester_user_id == session['user_two']:
        requester_problem_ids = session['user_two_questions']
        partner_problem_ids = session['user_one_questions']
    
    requester_problems = []
    partner_problems = []

    # get own problems
    for question_id in requester_problem_ids:
        question_id = question_id.strip()
        question = db.collection('questions').document(question_id).get().to_dict()
        if question:
            requester_problems.append({"question": question["question_prompt"]})

    # get partner problems
    for question_id in partner_problem_ids:
        question_id = question_id.strip()
        question = db.collection('questions').document(question_id).get().to_dict()
        if question:
            requester_problems.append({"question": question["question_prompt"],
                                        "answer": question["question_answer"]})

    return jsonify({'problem_set': requester_problems, 'partner_problem_set' : partner_problems}), 200



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1234))
    app.run(host='0.0.0.0', port=port)
