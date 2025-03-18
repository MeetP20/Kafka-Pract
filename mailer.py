from kafka import KafkaConsumer, KafkaProducer
import psycopg2
import json

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = "your-aiven-kafka-host:your-port"  # Example: "your-project.aivencloud.com:12345"

# SSL Certificates from Aiven
SSL_CERT = "/path/to/service.cert"  # Update with actual path
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

# PostgreSQL Configuration
DB_CONFIG = {
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    "host": "your_db_host",
    "port": "your_db_port"
}

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    INSERT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SSL",
    ssl_cafile=SSL_CA,
    ssl_certfile=SSL_CERT,
    ssl_keyfile=SSL_KEY,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="inserter"
)

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SSL",
    ssl_cafile=SSL_CA,
    ssl_certfile=SSL_CERT,
    ssl_keyfile=SSL_KEY,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def insert_order(email, address, product, quantity):
    """ Inserts order details into PostgreSQL database """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = "INSERT INTO orders (email, address, product, quantity) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (email, address, product, quantity))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Insert Error: {e}")
        return False

print("Inserter Microservice is running...")

# Consume messages from the insert topic
while True:
    order_data = consumer.poll(timeout_ms=1000)
    email = order_data["email"]
    address = order_data["address"]
    product = order_data["product"]
    quantity = order_data["quantity"]

    print(f"Inserting order: {order_data}")

    if insert_order(email, address, product, quantity):
        # Publish success message to mails topic
        mail_data = {"email": email, "status": "Order Placed Successfully"}
        producer.send(MAILS_TOPIC, value=mail_data)
        producer.flush()
        print(f"Inserted order and notified user: {email}")
    else:
        print(f"Failed to insert order: {order_data}")
