# Upload questions from csv to firebase
import os
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid

# Use the application default credentials
cred = credentials.Certificate('../firebase_key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def get_dir_csv_files():
    files = os.listdir()
    res = []

    for file in files:
        ext = file.rsplit('.', 1)[-1]

        if ext == 'csv':
            res.append(file)

    return res

"""
return dict structure
{
    "subject1": [
        (question1, answer1),
        (question2, answer2),
    ],
    "subject2": [
        (question1, answer1),
        (question2, answer2),
    ]
}
"""
def parse_csv_to_dict(csv_files):
    res = {}

    for file in csv_files:
        subject = file.rsplit('.', 1)[0]
        question_list = []


        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                else:
                    line_count += 1
                    question_list.append((row[0], row[1]))


        res[subject] = question_list

    return res

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)


def firebase_upload(question_dict):
    coll_ref = db.collection(u'questions')
    delete_collection(coll_ref, 5)

    for subject, questions in question_dict.items():
        for question_prompt, question_answer in questions:
            task_id = str(uuid.uuid4())
            doc_ref = db.collection('questions').document()
            doc_ref.set({
                "question_answer": question_answer,
                "question_prompt": question_prompt,
                "subject": subject
            })


files = get_dir_csv_files()
question_dict = parse_csv_to_dict(files)
firebase_upload(question_dict)
