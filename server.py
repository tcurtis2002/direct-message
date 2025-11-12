import pika
import time

# -------------------------------
# Reliable RabbitMQ Connection
# -------------------------------
def connect():
    """Try to connect to RabbitMQ, retrying every 3 seconds if it fails."""
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost')
            )
            channel = connection.channel()
            print("✅ Server connected to RabbitMQ")
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("❌ Server connection failed. Retrying in 3 seconds...")
            time.sleep(3)

# -------------------------------
# Main Server Logic
# -------------------------------
def main():
    queue_name = 'chat_queue'
    connection, channel = connect()
    channel.queue_declare(queue=queue_name)

    print("💬 RabbitMQ Chat Server is running... Waiting for messages.")

    while True:
        try:
            method_frame, properties, body = channel.basic_get(queue=queue_name, auto_ack=True)
            if body:
                print(f"📩 {body.decode()}")
            else:
                time.sleep(1)  # No message, check again
        except pika.exceptions.StreamLostError:
            print("⚠️ Stream lost — reconnecting server...")
            connection, channel = connect()
            channel.queue_declare(queue=queue_name)
        except pika.exceptions.ChannelWrongStateError:
            print("⚠️ Channel closed unexpectedly — reconnecting server...")
            connection, channel = connect()
            channel.queue_declare(queue=queue_name)
        except KeyboardInterrupt:
            print("\n👋 Server shutting down gracefully.")
            break
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            time.sleep(2)

    connection.close()
    print("🔌 Server connection closed. Goodbye!")

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    main()