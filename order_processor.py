from kafka import KafkaConsumer, KafkaProducer
import json
import time

# Kafka configurations
ORDERDATA_TOPIC = "orderdata"
INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

# Simulating stock (for one product)
STOCK = 20  # Adjust stock as needed

# Kafka Producer (for sending messages)
KAFKA_BOOTSTRAP_SERVERS = "your-aiven-kafka-host:your-port"  # Example: "your-project.aivencloud.com:12345"

# SSL Certificates from Aiven
SSL_CERT = "/path/to/service.cert"  # Update with actual path
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

# Create Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SSL",
    ssl_cafile=SSL_CA,
    ssl_certfile=SSL_CERT,
    ssl_keyfile=SSL_KEY,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_order(order):
    global STOCK  # Access global stock
    email = order["email"]
    product = order["product"]
    quantity = order["quantity"]

    if STOCK >= quantity:
        STOCK -= quantity  # Deduct stock
        print(f"Order confirmed for {email}, Remaining stock: {STOCK}")

        # Publish order details to the insert topic
        producer.send(INSERT_TOPIC, value=order)
        producer.flush()

    else:
        print(f"Order failed for {email}, product out of stock.")
        
        # Notify user of failure
        mail_data = {"email": email, "status": "Out of Stock"}
        producer.send(MAILS_TOPIC, value=mail_data)
        producer.flush()

# Kafka Consumer (for receiving orders)
consumer = KafkaConsumer(
    ORDERDATA_TOPIC,
    security_protocol="SSL",
    ssl_cafile=SSL_CA,
    ssl_certfile=SSL_CERT,
    ssl_keyfile=SSL_KEY,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="order-processor" 
)

print("Order Processor is running...")

# Listen for new orders
while True:
    messages = consumer.poll(timeout_ms=500)
    if not messages:  # If no messages, continue polling
        continue  

    for records in messages.values():  # Get list of messages
        for record in records:
            try:
                order = json.loads(record.value)  # Extract message data
                print(f"Received order: {order}")
                process_order(order)
                consumer.commit()
                






