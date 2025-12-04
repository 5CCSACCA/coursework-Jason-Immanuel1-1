import pika
import json
import os
import time
import logging
from typing import Any

from pika import BlockingConnection, exceptions

from predictor import BitNetCaloriePredictor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalorieConsumer:
    """
    RabbitMQ consumer that listens to calorie request messages, predicts calories
    using BitNetCaloriePredictor, and sends responses back to a calorie_response queue.

    Attributes:
        rabbitmq_host (str): Hostname of the RabbitMQ server.
        api_url (str): Optional API URL for external interactions.
        max_retries (int): Maximum number of connection retries.
        retry_delay (int): Delay between retries in seconds.
        connection (pika.BlockingConnection): RabbitMQ connection object.
        channel (pika.channel.Channel): RabbitMQ channel.
        predictor (BitNetCaloriePredictor): Calorie prediction model instance.
    """

    def __init__(self, max_retries: int = 10, retry_delay: int = 5):
        """
        Initialize the consumer, connect to RabbitMQ, declare queues, and
        initialize the calorie predictor.

        Args:
            max_retries (int, optional): Max connection retries. Defaults to 10.
            retry_delay (int, optional): Delay between retries (seconds). Defaults to 5.
        """
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.api_url = os.getenv("FOOD_API_URL", "http://food_prediction_service:8000")
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.connection = self.__connect_with_retry()
        self.channel = self.connection.channel()

        # Declare durable queues
        self.channel.queue_declare(queue="calorie_request", durable=True)
        self.channel.queue_declare(queue="calorie_response", durable=True)

        logger.info("Initializing BitNet Calorie Predictor")
        self.predictor = BitNetCaloriePredictor()
        logger.info("BitNet Calorie Predictor initialized successfully")

    def __connect_with_retry(self) -> BlockingConnection | None:
        """
        Connect to RabbitMQ with retry logic.

        Returns:
            pika.BlockingConnection: Established RabbitMQ connection.

        Raises:
            pika.exceptions.AMQPConnectionError: If connection cannot be established.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Connecting to RabbitMQ at {self.rabbitmq_host} "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.rabbitmq_host,
                        port=5672,
                        connection_attempts=3,
                        retry_delay=2,
                        heartbeat=600,
                        blocked_connection_timeout=300
                    )
                )
                logger.info("Successfully connected to RabbitMQ")
                return connection
            except pika.exceptions.AMQPConnectionError as e:
                logger.warning(f"Connection attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached. Could not connect to RabbitMQ")
                    raise
        return None

    def start(self):
        """
        Start consuming messages from the 'calorie_request' queue.
        """
        logger.info("Starting to consume messages from 'calorie_request' queue'")
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue="calorie_request",
            on_message_callback=self.process
        )

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error while consuming: {e}")
            raise
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")

    def process(self, ch: Any, method: Any, properties: Any, body: bytes):
        """
        Callback function to process a single calorie request message.

        Args:
            ch: RabbitMQ channel.
            method: Delivery method.
            properties: Message properties.
            body (bytes): Message body containing JSON with 'doc_id' and 'food_name'.
        """
        try:
            message = json.loads(body)
            doc_id = message.get("doc_id")
            food_name = message.get("food_name")

            logger.info(f"Processing message - doc_id: {doc_id}, food_name: {food_name}")

            # Predict calories
            calories = self.predictor.predict_calories(food_name)
            logger.info(f"Predicted calories for '{food_name}': {calories}")

            # Send response back
            response_body = json.dumps({
                "doc_id": doc_id,
                "calories": calories
            })
            self.channel.basic_publish(
                exchange="",
                routing_key="calorie_response",
                body=response_body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info(f"Sent calorie response: {response_body}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


if __name__ == "__main__":
    try:
        consumer = CalorieConsumer()
        consumer.start()
    except Exception as exc:
        logger.error(f"Failed to start consumer: {exc}", exc_info=True)
        exit(1)

