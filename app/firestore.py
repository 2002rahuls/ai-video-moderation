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

SERVER_TIMESTAMP = firestore.firestore.SERVER_TIMESTAMP

SOURCE_INFO = {
    "updateSourceCF": "ai-video-moderation",
    "updateSource": "script",
    "version": firestore.firestore.Increment(1)
}


def fetch_failed_videos():
    return list(
        db.collection("UserVideos")
        .where("aiVideoModerationStatus", "==", "failed")
        .get()
    )


def update_video_result(doc_id: str, moderation_result: dict):
    db.collection("UserVideos").document(doc_id).update({
        "aiVideoModerationOutput": moderation_result,
        "aiVideoModerationStatus": moderation_result["moderationStatus"],
        "updatedAt": SERVER_TIMESTAMP,
        **SOURCE_INFO
    })