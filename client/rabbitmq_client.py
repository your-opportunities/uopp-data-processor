import logging
import time
import ssl

import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError, ConnectionClosedByBroker

logger = logging.getLogger(__name__)


class DefaultRabbitMQClient:
    def __init__(self, queue_name, delivery_mode, host, port, username, password, max_retries, retry_delay, use_ssl=False, virtual_host='/'):
        self.queue_name = queue_name
        self.delivery_mode = delivery_mode
        self.credentials = pika.PlainCredentials(username, password)
        
        # Configure connection parameters based on SSL requirement
        if use_ssl:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            self.parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=self.credentials,
                virtual_host=virtual_host,
                heartbeat=30,  # 30 second heartbeat
                connection_attempts=3,
                retry_delay=1,
                socket_timeout=5,
                blocked_connection_timeout=300,
                ssl_options=pika.SSLOptions(context)
            )
        else:
            self.parameters = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=self.credentials,
                virtual_host=virtual_host,
                heartbeat=30,  # 30 second heartbeat
                connection_attempts=3,
                retry_delay=1,
                socket_timeout=5,
                blocked_connection_timeout=300
            )
        
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.connection = None
        self.channel = None
        self.declared_queues = {}
        self.consumer_tag = None
        self._running = False

    def setup_connection(self):
        """Setup connection with automatic retry logic"""
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                if self.connection and not self.connection.is_closed:
                    self.close_connection()
                
                logger.info(f"Attempting to connect to RabbitMQ at {self.parameters.host}:{self.parameters.port} (SSL: {hasattr(self.parameters, 'ssl_options')})")
                self.connection = pika.BlockingConnection(self.parameters)
                self.channel = self.connection.channel()
                
                # Enable publisher confirms for reliable message delivery
                self.channel.confirm_delivery()
                
                logger.info("RabbitMQ setup completed successfully.")
                return True
                
            except (AMQPConnectionError, ConnectionClosedByBroker) as e:
                retry_count += 1
                logger.warning(f"Failed to connect to RabbitMQ (attempt {retry_count}/{self.max_retries}): {e}")
                if retry_count < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to connect to RabbitMQ after {self.max_retries} attempts")
                    return False
            except Exception as e:
                logger.error(f"Unexpected error during connection setup: {e}")
                return False
        return False

    def close_connection(self):
        """Close connection gracefully"""
        try:
            if self.channel and not self.channel.is_closed:
                self.channel.close()
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            logger.info("RabbitMQ connection closed.")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

    def _ensure_connection(self):
        """Ensure connection is active, reconnect if necessary"""
        if not self.connection or self.connection.is_closed:
            logger.info("Connection is closed, attempting to reconnect...")
            if not self.setup_connection():
                raise AMQPConnectionError("Failed to reconnect to RabbitMQ")

    def produce_message(self, message, queue_name):
        """Produce message with automatic reconnection"""
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                self._ensure_connection()
                
                if queue_name not in self.declared_queues:
                    self.channel.queue_declare(queue=queue_name, durable=True)
                    self.declared_queues[queue_name] = True
                    logger.info("Queue declared successfully.")
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=self.delivery_mode,
                    )
                )
                logger.info("Message produced successfully.")
                return True
                
            except (AMQPConnectionError, AMQPChannelError, ConnectionClosedByBroker) as e:
                logger.error(f"Error producing message: {e}")
                retry_count += 1
                if retry_count <= self.max_retries:
                    time.sleep(self.retry_delay)
                    # Clear declared queues to force redeclaration on reconnect
                    self.declared_queues = {}
                else:
                    logger.error("Maximum retry limit reached, message could not be produced.")
                    break
            except Exception as e:
                logger.error(f"Unexpected error producing message: {e}")
                break
        return False

    def register_message_consumer(self, handler, queue_name):
        """Register message consumer with enhanced error handling"""
        def on_message(channel, method, properties, body):
            logger.info(f"Consumed message from '{queue_name}': {body}")
            try:
                handler(body)
                # Manually acknowledge the message for better control
                if not self.channel.is_closed:
                    self.channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error consuming message: {e}")
                # Negative acknowledge the message on error
                if not self.channel.is_closed:
                    self.channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        try:
            self._ensure_connection()
            
            # Set QoS for better message distribution
            self.channel.basic_qos(prefetch_count=1)
            
            self.consumer_tag = self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message,
                auto_ack=False  # Manual acknowledgment for better control
            )
            logger.info(f"Registered message handler and started consumer for queue {queue_name}.")
            
        except Exception as e:
            logger.error(f"Failed to register message consumer: {e}")
            raise

    def start_consuming(self):
        """Start consuming messages with automatic reconnection - runs continuously until explicitly stopped"""
        self._running = True
        consecutive_failures = 0
        max_consecutive_failures = 5  # Maximum consecutive failures before longer wait
        
        logger.info("Starting continuous message consumption...")
        
        while self._running:
            try:
                logger.info("Starting message consumption...")
                self._ensure_connection()
                
                # Reset consecutive failures on successful connection
                consecutive_failures = 0
                
                # Start consuming - this will block until connection is lost or stopped
                self.channel.start_consuming()
                
            except (AMQPConnectionError, ConnectionClosedByBroker) as e:
                consecutive_failures += 1
                logger.warning(f"Connection lost during consumption (failure #{consecutive_failures}): {e}")
                
                if self._running:
                    # Exponential backoff for consecutive failures
                    wait_time = min(self.retry_delay * (2 ** (consecutive_failures - 1)), 60)  # Max 60 seconds
                    logger.info(f"Attempting to reconnect in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    break
                    
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Unexpected error during message consumption (failure #{consecutive_failures}): {e}")
                
                if self._running:
                    # Exponential backoff for consecutive failures
                    wait_time = min(self.retry_delay * (2 ** (consecutive_failures - 1)), 60)  # Max 60 seconds
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    break
        
        logger.info("Message consumption stopped.")

    def stop_consuming(self):
        """Stop consuming messages gracefully - only call this when you want to stop the consumer"""
        logger.info("Stopping message consumption...")
        self._running = False
        try:
            if self.consumer_tag and self.channel and not self.channel.is_closed:
                self.channel.basic_cancel(self.consumer_tag)
                logger.info("Stopped consuming messages.")
        except Exception as e:
            logger.warning(f"Error stopping consumption: {e}")
