import asyncio
from concurrent.futures import ThreadPoolExecutor
from app.firestore import fetch_failed_videos
from app.worker import process_video
from app.config import BATCH_SIZE


def main():
    docs = fetch_failed_videos()

    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        for doc in docs:
            executor.submit(asyncio.run, process_video(doc))


if __name__ == "__main__":
    main()
