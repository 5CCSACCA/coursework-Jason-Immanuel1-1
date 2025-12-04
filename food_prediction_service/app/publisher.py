import json
import logging
import os
from typing import Dict

import pika

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    """
    RabbitMQ publisher for sending messages to a specified queue.

    Connects to RabbitMQ using environment-configured host and queue,
    publishes JSON messages with persistence, and handles connection errors.
    """

    def __init__(self):
        """
        Initialize the RabbitMQPublisher.

        Environment variables:
            RABBITMQ_HOST (str): Hostname of RabbitMQ server (default: "localhost").
            RABBITMQ_QUEUE (str): Queue name to publish messages (default: "calorie_request").

        Attributes:
            connection_params (pika.ConnectionParameters): Connection configuration.
        """
        self.host = os.getenv("RABBITMQ_HOST", "localhost")
        self.queue = os.getenv("RABBITMQ_QUEUE", "calorie_request")

        self.connection_params = pika.ConnectionParameters(
            host=self.host,
            heartbeat=600,
            blocked_connection_timeout=300
        )

    def publish(self, message: Dict):
        """
        Publish a message to the configured RabbitMQ queue.

        Args:
            message (dict): JSON-serializable message to send.

        Raises:
            Exception: If there is an error connecting to RabbitMQ or publishing the message.
        """
        connection = None
        try:
            # Establish connection and channel
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()

            # Ensure the queue exists
            channel.queue_declare(queue=self.queue, durable=True)

            # Publish message with persistence
            body = json.dumps(message)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2  # Make message persistent
                )
            )
            logger.info(f"Sent to queue '{self.queue}': {body}")

        except Exception as e:
            logger.error(f"Error publishing to RabbitMQ: {e}")
            raise
        finally:
            # Ensure the connection is safely closed
            if connection and not connection.is_closed:
                connection.close()
