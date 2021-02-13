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



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 80))
    app.run(host='0.0.0.0', port=port)
