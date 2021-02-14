# Upload questions from csv to firebase
import os
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random

# Use the application default credentials
cred = credentials.Certificate('../firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()



def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def generate_questions(subject):
    all_questions = db.collection('questions')\
                        .where('subject', '==', subject)\
                        .stream()

    question_list = []
    for question in all_questions:
        question_list.append(question.id)

    return random.choices(question_list, k=5)

def firebase_upload(question_dict):
    coll_ref = db.collection(u'sessions')
    delete_collection(coll_ref, 5)

    for subject, questions in question_dict.items():
        for question_prompt, question_answer in questions:
            doc_ref = db.collection('sessions').document()
            doc_ref.set({
                "question_answer": question_answer,
                "question_prompt": question_prompt,
                "subject": subject
            })

def gen_sessions():
    coll_ref = db.collection(u'sessions')

    # delete_collection(coll_ref, 5)

    for _ in range(5):
        schedule_session()

def schedule_session():
    name_ids = random.sample(range(0, len(names)), 2)
    name_1 = names[name_ids[0]]
    name_2 = names[name_ids[1]]
    course = "Datastructures and Algorithms"

    res = {
        "course": course,
        "meeting_time": "Later",
        "user_one_questions": generate_questions(course),
        "user_one": name_1,
        "user_two": name_2,
        "user_two_questions": generate_questions(course)
    }

    session_ref = db.collection('sessions').document()
    session_ref.set(res)


names = ["Justin", "Albert", "James", "Issack", "Nathaniel"]
time = ["Now", "Later"]

gen_sessions()