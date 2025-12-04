import pika
import json
import os
import time
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from pika import exceptions


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load Firebase credentials and initialize app
firebase_key_path = os.getenv("FIREBASE_KEY_PATH", "firebase-key.json")

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()


class CalorieResponseListener:
    """
    Worker that listens to RabbitMQ calorie response messages and updates Firestore.

    Continuously consumes messages from the 'calorie_response' queue. Each message
    should contain a JSON payload with 'doc_id' and 'calories'. Updates Firestore
    documents or uses a shared `update_prediction` function if available.
    """

    def __init__(self):
        """
        Initialize the listener with RabbitMQ host and queue.

        Attributes:
            host (str): RabbitMQ host address from environment variable or default 'rabbitmq'.
            queue_name (str): Name of the RabbitMQ queue to consume messages from.
        """
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.queue_name = "calorie_response"

    def start(self) -> None:
        """
        Start the worker loop to consume messages from RabbitMQ.

        Connects to RabbitMQ, declares the queue, and sets up the message callback.
        Includes retry logic for connection failures or unexpected errors.
        """
        while True:
            try:
                # Connect to RabbitMQ
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(host=self.host)
                )
                channel = connection.channel()
                channel.queue_declare(queue=self.queue_name, durable=True)

                logging.info(f"Worker connected to RabbitMQ at {self.host}")
                logging.info(f"Waiting for messages in '{self.queue_name}'")

                # Set up message consumption
                channel.basic_consume(
                    queue=self.queue_name,
                    on_message_callback=self.__process_response,
                    auto_ack=True
                )
                channel.start_consuming()

            except pika.exceptions.AMQPConnectionError:
                logging.warning("Connection failed, retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                logging.error(f"Unexpected error: {e}, retrying in 5 seconds...")
                time.sleep(5)

    def __process_response(self, ch, method, props, body) -> None:
        """
        Process a single calorie response message.

        Parses the message JSON, extracts 'doc_id' and 'calories', and updates Firestore.
        Logs invalid messages or errors. Uses `update_prediction` function if available.

        Args:
            ch: RabbitMQ channel
            method: Delivery method
            props: Message properties
            body (bytes): JSON payload containing 'doc_id' and 'calories'
        """
        try:
            data = json.loads(body)
            doc_id = data.get("doc_id")
            calories = data.get("calories")

            if doc_id and calories:
                logging.info(f"Received update for {doc_id}: {calories} kcal")

                # Update Firestore
                db.collection("predictions").document(doc_id).update({
                    "calories": calories
                })

            else:
                logging.warning("Received invalid data format: %s", data)

        except json.JSONDecodeError:
            logging.error("Failed to decode JSON message: %s", body)
        except Exception as e:
            logging.error("Error processing message: %s", e)


if __name__ == "__main__":
    listener = CalorieResponseListener()
    listener.start()

