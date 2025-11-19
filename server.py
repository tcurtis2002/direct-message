import pika
import time

# -------------------------------
# Reliable RabbitMQ Connection
# -------------------------------
SERVER_IP = '172.20.210.46'
RABBIT_USER = 'chatuser'
RABBIT_PASS = 'password123'

def connect():
    creds = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)

    params = pika.ConnectionParameters(
        host=SERVER_IP,
        credentials=creds
    )

    while True:
        try:
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("❌ Connection failed. Retrying in 3 seconds...")
            time.sleep(3)

# -------------------------------
# Main Server Logic (monitor)
# -------------------------------
def main():
    connection, channel = connect()

    # Use the SAME fanout exchange as the clients
    channel.exchange_declare(exchange='chat', exchange_type='fanout')

    # Server gets its own temporary queue too
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Bind server's queue to the exchange
    channel.queue_bind(exchange='chat', queue=queue_name)

    print("💬 RabbitMQ Chat Server monitor is running... Waiting for messages.")

    def callback(ch, method, properties, body):
        print(f"📩 [SERVER RECEIVED] {body.decode()}")

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n👋 Server shutting down gracefully.")
    finally:
        connection.close()
        print("🔌 Server connection closed. Goodbye!")

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    main()
