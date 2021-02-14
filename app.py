import random
from flask import Flask, jsonify, request
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Use the application default credentials
cred = credentials.Certificate('./firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)


@app.route('/')
@cross_origin()
def home_endpoint():
    return 'Hello World! 123'


@app.route('/get_problems', methods=['GET'])
@cross_origin()
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

    return jsonify({'problem_set': requester_problems, 'partner_problem_set': partner_problems}), 200


@app.route('/schedule_session', methods=['POST'])
@cross_origin()
def schedule_session():
    req_json = request.get_json()
    user_id = req_json["user_id"] if "user_id" in req_json else None
    meeting_time = req_json["meeting_time"] if "meeting_time" in req_json else None
    course = req_json["course"] if "course" in req_json else None

    if user_id is None or meeting_time is None or course is None:
        return "Malformed request", 400

    # If theres others waiting for that meeting time, match them
    free_spots = []
    all_sessions = db.collection('sessions')\
                        .where('meeting_time', '==', meeting_time)\
                        .where('course', '==', course)\
                        .stream()

    for session in all_sessions:
        session_dict = session.to_dict()
        if session_dict["user_two"] is None:
            session_dict["session_id"] = session.id
            free_spots.append(session_dict)

        if session_dict["user_one"] == user_id or session_dict["user_two"] == user_id:
            return "Already booked this date", 201

    if len(free_spots) > 0:
        session_id = free_spots[0]["session_id"]
        session_ref = db.collection('sessions').document(session_id)
        session_ref.update({
            "user_two": user_id
        })

        return "Found a match", 201
    else:
        session_ref = db.collection('sessions').document()
        session_ref.set({
            "user_one": user_id,
            "user_two": None,
            "meeting_time": meeting_time,
            "course": course,
            "user_one_questions": generate_questions(course),
            "user_two_questions": generate_questions(course)
        })

        return "Looking for a match", 201


def generate_questions(subject):
    all_questions = db.collection('questions')\
                        .where('subject', '==', subject)\
                        .stream()

    question_list = []
    for question in all_questions:
        question_list.append(question.id)

    return random.choices(question_list, k=5)

def get_formatted_questions_with_ans(questions):
    res = ""

    for i, question_id in enumerate(questions):
        question = db.collection('questions').document(question_id).get().to_dict()
        if question:
            res += f"## Question {i + 1}  \n**Prompt:**  \n{question['question_prompt']}  \n\n**Answer:**  \n{question['question_answer']}  \n***\n"

    print(res)
    return res


@app.route('/get_all_sessions', methods=['GET'])
@cross_origin()
def get_all_sessions():
    if 'user_id' not in request.args:
        return "Malformed Request", 400

    user_id = request.args.get('user_id')

    if user_id is None:
        return "User ID not specified", 400

    results = {}
    # Get all sessions as session one
    sessions_as_user_one = db.collection('sessions') \
        .where('user_one', '==', user_id) \
        .stream()
    for session in sessions_as_user_one:
        sess = session.to_dict()
        sess['id'] = session.id
        sess['formatted_questions'] = get_formatted_questions_with_ans(sess["user_two_questions"])
        results[session.id] = sess

    # Get all sessions as session two
    sessions_as_user_two = db.collection('sessions') \
        .where('user_two', '==', user_id) \
        .stream()

    for session in sessions_as_user_two:
        sess = session.to_dict()
        sess['id'] = session.id
        sess['formatted_questions'] = get_formatted_questions_with_ans(sess["user_one_questions"])
        results[session.id] = sess    
        

    return jsonify(results), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
