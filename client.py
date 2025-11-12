import pika
import threading
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
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("❌ Connection failed. Retrying in 3 seconds...")
            time.sleep(3)

# -------------------------------
# Continuous Message Receiver
# -------------------------------
def receive_messages(queue_name):
    """Continuously receive messages from RabbitMQ with its own connection."""
    while True:
        try:
            connection, channel = connect()
            channel.queue_declare(queue=queue_name)
            print("👂 Listening for messages...")

            for method, properties, body in channel.consume(queue=queue_name, inactivity_timeout=10):
                if body:
                    print("\n💬", body.decode())
                else:
                    pass  # no new message during timeout

        except pika.exceptions.StreamLostError:
            print("⚠️ Stream lost — reconnecting listener...")
            time.sleep(3)
            continue
        except pika.exceptions.ConnectionClosed:
            print("⚠️ Connection closed — reconnecting listener...")
            time.sleep(3)
            continue
        except Exception as e:
            print(f"⚠️ Receiver error: {e}")
            time.sleep(3)
            continue

# -------------------------------
# Main Client Logic
# -------------------------------
def main():
    queue_name = 'chat_queue'
    print("✅ Starting RabbitMQ Chat Client")

    # Start the receiver thread (it manages its own connection)
    receiver_thread = threading.Thread(target=receive_messages, args=(queue_name,))
    receiver_thread.daemon = True
    receiver_thread.start()

    # Sender connection (main thread)
    connection, channel = connect()
    channel.queue_declare(queue=queue_name)

    print("\nType your message and press Enter. Type 'exit' to quit.")
    username = input("Enter your username: ")

    while True:
        try:
            message = input(f"{username}: ")
            if message.lower() == "exit":
                break

            # Reconnect if channel closed
            if not channel.is_open:
                print("⚠️ Sender channel closed — reconnecting...")
                connection, channel = connect()
                channel.queue_declare(queue=queue_name)

            full_message = f"{username}: {message}"
            channel.basic_publish(exchange='', routing_key=queue_name, body=full_message)

        except pika.exceptions.ChannelWrongStateError:
            print("⚠️ Sender channel error — reconnecting...")
            connection, channel = connect()
            channel.queue_declare(queue=queue_name)
        except KeyboardInterrupt:
            print("\n👋 Exiting chat.")
            break
        except Exception as e:
            print("⚠️ Sender error:", e)
            time.sleep(2)

    connection.close()
    print("🔌 Connection closed. Goodbye!")

# -------------------------------
# Run Client
# -------------------------------
if __name__ == "__main__":
    main()