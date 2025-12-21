from os import getenv

from firebase_admin import firestore, initialize_app
from firebase_functions import https_fn, logger, options, scheduler_fn
from google.cloud.firestore import (
    Client as FireStoreClient,
)
from google.cloud.firestore import (
    DocumentReference,
    DocumentSnapshot,
    Increment,
)
from logfire import configure, instrument_httpx

configure(service_name="StreamStorm")
instrument_httpx()

from lib.DiscordWebhook import send_discord_webhook

ALLOWED_HOSTS: list[str] = getenv("ALLOWED_HOSTS").split(",")

initialize_app()

options.set_global_options(
    region=getenv("FUNCTIONS_REGION"),
    enforce_app_check=True,
)


def get_doc_ref(collection: str, document: str) -> DocumentReference:
    db: FireStoreClient = firestore.client()
    return db.collection(collection).document(document)


@https_fn.on_call(
    cors=options.CorsOptions(
        cors_origins=ALLOWED_HOSTS, cors_methods=["POST", "OPTIONS"]
    )
)
def visit_count(req: https_fn.Request) -> https_fn.Response:
    logger.info("Visit count function triggered...")

    doc_ref: DocumentReference = get_doc_ref("streamstorm", "counts")
    doc_ref.update({"visit": Increment(1)})
    doc: DocumentSnapshot = doc_ref.get()
    count: int = doc.to_dict().get("visit", 0)

    send_discord_webhook("visit")

    logger.info(f"New visit count: {count}")
    return {"success": True, "count": count}


@https_fn.on_call(
    cors=options.CorsOptions(
        cors_origins=ALLOWED_HOSTS, cors_methods=["POST", "OPTIONS"]
    )
)
def downloads_count(req: https_fn.Request) -> https_fn.Response:
    logger.info("Downloads count function triggered...")

    data: dict = req.data
    logger.info(f"Request data: {data}")
    doc_ref: DocumentReference = get_doc_ref("streamstorm", "counts")

    if data.get("mode") == "set":
        doc_ref.update({"downloads": Increment(1)})
        send_discord_webhook("download")

    doc: DocumentSnapshot = doc_ref.get()
    count: int = doc.to_dict().get("downloads", 0)

    logger.info(f"New downloads count: {count}")
    return {"success": True, "count": count}


@scheduler_fn.on_schedule(schedule="0 0 * * *")  # Daily at midnight UTC
def ping_mongodb_cluster(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Function to ping the MongoDB cluster to ensure it doesn't go idle.
    """
    try:
        from pymongo import MongoClient
        from pymongo.synchronous.collection import Collection
        from pymongo.synchronous.database import Database

        with MongoClient(getenv("MONGO_DB_URI")) as client:
            client.admin.command("ping")
            logger.info("MongoDB cluster pinged successfully.")

            db: Database = client["DGUPDATER"]
            collection: Collection = db["StreamStorm"]

            collection.find_one({"_id": "StreamStorm_config"})
            logger.info("MongoDB collection accessed successfully.")

    except Exception as e:
        logger.error(f"Error pinging MongoDB cluster: {e}")

    finally:
        logger.info("Function ping_mongodb_cluster has been executed")
