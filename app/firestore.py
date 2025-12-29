import os
import firebase_admin
from firebase_admin import credentials, firestore

# ---- STAGE ----
SERVICE_ACCOUNT_FILE = os.path.join(
    os.path.dirname(__file__),
    "genailearning-3bd13-firebase-adminsdk.json"  
)


# Initialize Firebase Admin SDK
if not firebase_admin._apps:  # Prevent re-initialization
    cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
