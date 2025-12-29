import sys
import os
import csv
import requests
import concurrent.futures
from pathlib import Path
import asyncio  # FIX: Import asyncio
import time # ⭐️ Added for timestamp
import uuid # ⭐️ Added for random string
from itertools import islice
# Use typing and import shared Firestore initialization from app.firestore
from typing import Iterable, List, Any
from google.api_core.exceptions import DeadlineExceeded
from .firestore import db, SERVER_TIMESTAMP as server_timestamp, SOURCE_INFO as sourceInfo

# --- Local Imports ---
# FIX: Use a relative import, assuming the file is in the same 'POCs' directory
from pipeline import moderate_video

# Firestore client and constants are imported from app.firestore above

# --- Directory Setup ---
LOCAL_VIDEO_DIR = Path("downloaded_videos")
LOCAL_VIDEO_DIR.mkdir(exist_ok=True)
ERROR_CSV_DIR = Path("batch_errors")
ERROR_CSV_DIR.mkdir(exist_ok=True)


def download_video(video_url: str, file_name: str) -> str:
    """
    Downloads video from URL and stores locally.
    """
    local_path = LOCAL_VIDEO_DIR / file_name
    try:
        response = requests.get(video_url, stream=True, timeout=60)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return str(local_path)
    except Exception as e:
        # Clean up partially downloaded file on failure
        if os.path.exists(local_path):
            os.remove(local_path)
        raise RuntimeError(f"❌ Failed to download video: {e}")


# FIX: This is now the ASYNC worker containing the core logic
async def process_video_async(doc_snapshot):
    """
    Processes one Firestore document asynchronously.
    """
    doc_id = doc_snapshot.id
    data = doc_snapshot.to_dict()
    video_url = data.get("videoUrl")
    aiVideoModerationStatus = data.get("aiVideoModerationStatus")
    initialSize = data.get("initialSize")
    isDeleted = data.get("isDeleted")
    local_path = None # Ensure local_path is defined for the finally block
    if aiVideoModerationStatus == "failed" or None:
        if isDeleted is False:
            if initialSize != 0:
                if video_url is not None:

                    try:
                        file_name = f"{doc_id}.mp4"
                        local_path = download_video(video_url, file_name)

                        moderation_result = await moderate_video(local_path)
                        moderation_status = moderation_result["moderationStatus"]

                        # FIX: Removed the redundant if/else block
                        db.collection("UserVideos").document(doc_id).update({
                            "aiVideoModerationOutput": moderation_result,
                            "aiVideoModerationStatus": moderation_status,
                            "updatedAt": server_timestamp,
                            **sourceInfo
                        })

                        return {"id": doc_id, "status": "success", "moderation": moderation_result}
                    except Exception as e:
                        return {"id": doc_id, "status": "failed", "error": str(e)}
                    finally:
                        # Ensure temporary video file is always cleaned up
                        if local_path and os.path.exists(local_path):
                            os.remove(local_path)
                else:
                    return {"id": doc_id, "status": "failed", "error": "video Url not present"}
            else:
                return {"id": doc_id, "status": "failed", "error": "initial size is 0"}
        else:
            return {"id": doc_id, "status": "failed", "error": "deleted"}
    
        
    else:
        return {"id": doc_id, "status": "failed", "error": "Already Processed"}



# FIX: This is the SYNCHRONOUS wrapper for the ThreadPoolExecutor
def process_video_sync_wrapper(doc_snapshot):
    """
    Runs the async video processing task within a new asyncio event loop.
    """
    return asyncio.run(process_video_async(doc_snapshot))


def chunk_iterable(iterable: Iterable, size: int) -> Iterable[List[Any]]:
    """
    Yields successive n-sized chunks from an iterable.
    This is memory-efficient as it doesn't load the whole iterable into memory.
    """
    iterator = iter(iterable)
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            return
        yield chunk

# def process_batch_incrementally(batch_size: int = 8):
#     """
#     Fetch documents, process them in parallel chunks, and create a separate CSV
#     report for each completed chunk.
#     """
#     query = db.collection("UserVideos").where("status", "==", "WAITING") #.limit(50)
    
#     # Wrap the document stream generation in a try-except block
#     try:
#         docs_stream = query.stream()
        
#         # ⭐️ 1. Process the document stream in chunks
#         for i, doc_chunk in enumerate(chunk_iterable(docs_stream, batch_size)):
#             batch_number = i + 1
#             print(f"--- Processing Batch #{batch_number} ({len(doc_chunk)} documents) ---")
            
#             batch_results = []
#             # ⭐️ 2. The ThreadPoolExecutor now processes only one chunk at a time
#             with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
#                 futures = [executor.submit(process_video_sync_wrapper, doc) for doc in doc_chunk]
#                 for future in concurrent.futures.as_completed(futures):
#                     batch_results.append(future.result())

#             if not batch_results:
#                 print(f"Batch #{batch_number} completed with no results to report.")
#                 continue # Move to the next chunk

#             # --- CSV Reporting for the current batch ---
#             report_rows = []
#             for r in batch_results:
#                 row = {"id": r.get("id"), "status": r.get("status")}
#                 if r.get("status") == "success":
#                     moderation_data = r.get("moderation", {})
#                     row.update(moderation_data)
#                 else:
#                     row["error"] = r.get("error")
#                 report_rows.append(row)

#             all_headers = set()
#             for row in report_rows:
#                 all_headers.update(row.keys())
            
#             ordered_headers = sorted(list(all_headers))
#             # Ensure critical columns are first for readability
#             for col in ["id", "status", "error", "moderationStatus", "reason"]:
#                 if col in ordered_headers:
#                     ordered_headers.remove(col)
#                     ordered_headers.insert(0, col)

#             # ⭐️ 3. Create a unique CSV file for each chunk
#             timestamp_ms = int(time.time() * 1000)
#             unique_file_name = f"batch_report_part_{batch_number}_{timestamp_ms}.csv"
#             batch_file = ERROR_CSV_DIR / unique_file_name

#             with open(batch_file, "w", newline="", encoding="utf-8") as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=ordered_headers)
#                 writer.writeheader()
#                 writer.writerows(report_rows)
            
#             print(f"✅ Batch #{batch_number} Completed. Report saved to {batch_file}")
    
#     except DeadlineExceeded as e:
#         # Create a report for the failed query and then exit the function.
#         print(f"🚨 A query deadline was exceeded. The Firestore query timed out: {e}")
        
#         # Create a report to log the error.
#         timestamp_ms = int(time.time() * 1000)
#         error_file_name = f"query_error_report_{timestamp_ms}.csv"
#         error_file = ERROR_CSV_DIR / error_file_name
        
#         report_row = {
#             "error_type": "Query Deadline Exceeded",
#             "message": str(e),
#             "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
#         }
        
#         with open(error_file, "w", newline="", encoding="utf-8") as csvfile:
#             writer = csv.DictWriter(csvfile, fieldnames=report_row.keys())
#             writer.writeheader()
#             writer.writerow(report_row)
            
#         print(f"📄 An error report has been saved to {error_file}")
        
#     except Exception as e:
#         # A catch-all for any other unexpected errors.
#         print(f"🚨 An unexpected error occurred: {e}")
#         # Optionally, create a general error report here as well.
#         # ...
        
#     finally:
#         print("\n🎉 Process completed. Check reports for details.")
def process_batch_incrementally(batch_size: int = 8):
    """
    Fetch documents, process them in parallel chunks, and create a separate CSV
    report for each completed chunk.
    """
    # NOTE: Using .get() is suitable for smaller result sets.
    # If the number of 'WAITING' videos can be very large, this may cause memory issues.
    query = db.collection("UserVideos").where("aiVideoModerationStatus", "==", "failed") #.limit(50)
    
    docs_list = None
    max_retries = 3
    retry_delay_seconds = 5
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to fetch documents from Firestore (Attempt {attempt + 1}/{max_retries})...")
            docs_list = list(query.get()) # Use .get() and convert to a list
            print(f"✅ Successfully fetched {len(docs_list)} documents from Firestore.")
            break  # Exit the retry loop on success
            
        except DeadlineExceeded as e:
            # .get() will raise this error directly on a timeout.
            print(f"🚨 A DeadlineExceeded error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print("❌ Max retries reached. Giving up.")
                _create_error_report("Firestore .get() Failed", str(e))
                return
        
        except Exception as e:
            # Catch-all for any other unexpected errors during the fetch
            print(f"🚨 An unexpected error occurred: {e}")
            _create_error_report("Unexpected .get() Error", str(e))
            return

    # Check if we got a list of documents before proceeding
    if docs_list is None:
        print("🛑 Could not fetch documents from Firestore after multiple retries. Exiting.")
        return

    # --- The rest of your processing logic is now simplified ---
    # The chunking and parallel processing can now work directly on the list.
    try:
        for i, doc_chunk in enumerate(chunk_iterable(docs_list, batch_size)):
            batch_number = i + 1
            print(f"--- Processing Batch #{batch_number} ({len(doc_chunk)} documents) ---")
            
            # The rest of your code for processing, thread pooling, and reporting
            batch_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = [executor.submit(process_video_sync_wrapper, doc) for doc in doc_chunk]
                for future in concurrent.futures.as_completed(futures):
                    batch_results.append(future.result())

            if not batch_results:
                print(f"Batch #{batch_number} completed with no results to report.")
                continue

            report_rows = []
            for r in batch_results:
                row = {"id": r.get("id"), "status": r.get("status")}
                if r.get("status") == "success":
                    moderation_data = r.get("moderation", {})
                    row.update(moderation_data)
                else:
                    row["error"] = r.get("error")
                report_rows.append(row)

            all_headers = set()
            for row in report_rows:
                all_headers.update(row.keys())
            
            ordered_headers = sorted(list(all_headers))
            for col in ["id", "status", "error", "moderationStatus", "reason"]:
                if col in ordered_headers:
                    ordered_headers.remove(col)
                    ordered_headers.insert(0, col)

            timestamp_ms = int(time.time() * 1000)
            unique_file_name = f"batch_report_part_{batch_number}_{timestamp_ms}.csv"
            batch_file = ERROR_CSV_DIR / unique_file_name

            with open(batch_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=ordered_headers)
                writer.writeheader()
                writer.writerows(report_rows)
            
            print(f"✅ Batch #{batch_number} Completed. Report saved to {batch_file}")

    except Exception as e:
        print(f"🚨 A critical error occurred during batch processing: {e}")
        _create_error_report("Critical Processing Error", str(e))
    finally:
        print("\n🎉 Process completed. Check reports for details.")

# The helper function remains the same
def _create_error_report(error_type, error_message):
    timestamp_ms = int(time.time() * 1000)
    error_file_name = f"error_report_{timestamp_ms}.csv"
    error_file = ERROR_CSV_DIR / error_file_name
    
    report_row = {
        "error_type": error_type,
        "message": error_message,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(error_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=report_row.keys())
        writer.writeheader()
        writer.writerow(report_row)
        
    print(f"📄 An error report has been saved to {error_file}")


if __name__ == "__main__":
    all_results = process_batch_incrementally()
    print(all_results)