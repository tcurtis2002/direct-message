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
# Continuous Message Receiver (pub/sub)
# -------------------------------
def receive_messages():
    """Continuously receive broadcast messages from RabbitMQ."""
    while True:
        try:
            connection, channel = connect()

            # 1️⃣ Declare a fanout exchange for broadcast
            channel.exchange_declare(exchange='chat', exchange_type='fanout')

            # 2️⃣ Each client gets its OWN temporary queue
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue

            # 3️⃣ Bind this queue to the exchange so it receives all messages
            channel.queue_bind(exchange='chat', queue=queue_name)

            print("👂 Listening for messages...")

            def callback(ch, method, properties, body):
                print("\n💬", body.decode())
                # reprint prompt indicator so input line looks nicer
                print("> ", end='', flush=True)

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=True
            )

            channel.start_consuming()

        except pika.exceptions.StreamLostError:
            print("⚠️ Stream lost — reconnecting listener...")
            time.sleep(3)
            continue
        except pika.exceptions.ConnectionClosed:
            print("⚠️ Connection closed — reconnecting listener...")
            time.sleep(3)
            continue
        except KeyboardInterrupt:
            print("\n👋 Listener shutting down.")
            try:
                connection.close()
            except Exception:
                pass
            break
        except Exception as e:
            print(f"⚠️ Receiver error: {e}")
            time.sleep(3)
            continue

# -------------------------------
# Main Client Logic (sender)
# -------------------------------
def main():
    print("✅ Starting RabbitMQ Broadcast Chat Client")

    username = input("Enter your username: ")

    # Start the receiver thread (it manages its own connection)
    receiver_thread = threading.Thread(target=receive_messages)
    receiver_thread.daemon = True
    receiver_thread.start()

    # Sender connection (main thread)
    connection, channel = connect()

    # Use the SAME fanout exchange for sending
    channel.exchange_declare(exchange='chat', exchange_type='fanout')

    print("\nType your message and press Enter. Type 'exit' to quit.")

    while True:
        try:
            message = input(f"{username}: ")
            if message.lower() == "exit":
                break

            full_message = f"{username}: {message}"
            # 🔥 Publish to the exchange, not a queue
            channel.basic_publish(
                exchange='chat',
                routing_key='',  # ignored for fanout
                body=full_message
            )

        except KeyboardInterrupt:
            print("\n👋 Exiting chat.")
            break
        except Exception as e:
            print("⚠️ Sender error:", e)
            time.sleep(2)

    try:
        connection.close()
    except Exception:
        pass
    print("🔌 Connection closed. Goodbye!")

# -------------------------------
# Run Client
# -------------------------------
if __name__ == "__main__":
    main()
