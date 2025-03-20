from kafka import KafkaConsumer, KafkaProducer
import psycopg2
import json

KAFKA_BOOTSTRAP_SERVERS = "your-aiven-kafka-host:your-port" 

SSL_CERT = "/path/to/service.cert"  # Update with actual path
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

DB_CONFIG = {
    "dbname": "your_database",
    "user": "your_user",
    "password": "your_password",
    "host": "your_db_host",
    "port": "your_db_port"
}

# consumer = KafkaConsumer(
#     INSERT_TOPIC,
#     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#     security_protocol="SSL",
#     ssl_cafile=SSL_CA,
#     ssl_certfile=SSL_CERT,
#     ssl_keyfile=SSL_KEY,
#     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
#     auto_offset_reset="earliest",
#     enable_auto_commit=False,
#     group_id="inserter"
# )

# producer = KafkaProducer(
#     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#     security_protocol="SSL",
#     ssl_cafile=SSL_CA,
#     ssl_certfile=SSL_CERT,
#     ssl_keyfile=SSL_KEY,
#     value_serializer=lambda v: json.dumps(v).encode("utf-8")
# )

producer = KafkaProducer(bootstrap_servers='localhost:29092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))


consumer = KafkaConsumer(
    INSERT_TOPIC,
    bootstrap_servers='localhost:29092',
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="order-processor" 
)

def insert_order(order_data):
    try:
        order_data = json.loads(order_data)
        email = order_data["email"]
        product = order_data["product"]
        address = order_data["address"]
        quantity = int(order_data["quantity"])

        print(email)
        print(product)
        print(address)
        print(quantity)
        # conn = psycopg2.connect(**DB_CONFIG)
        # cur = conn.cursor()
        # query = "INSERT INTO orders (email, address, product, quantity) VALUES (%s, %s, %s, %s)"
        # cur.execute(query, (email, address, product, quantity))
        # conn.commit()
        # cur.close()
        # conn.close()
        print("Record inserted")
        return True
    except Exception as e:
        print(f"Database Insert Error: {e}")
        return False

print("Inserter Microservice is running...")

while True:

    print("polling msg")
    messages = consumer.poll(timeout_ms=2000)

    if not messages:  
        continue  

    for message in messages.values():
        for record in message:
            try:
                order_data = json.dumps(record.value)
                get_email = json.loads(order_data)
                email = get_email["email"] 
                print(f"Inserting order: {order_data}")

                if insert_order(order_data):
                    mail_data = {"email": email, "status": "Order Placed Successfully"}
                    future = producer.send(MAILS_TOPIC, mail_data)
                    try:
                        record_metadata = future.get(timeout=10)  # Wait for confirmation with a timeout
                        print(f"✅ Message sent to {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
                    except KafkaTimeoutError as e:
                        print(f"❌ Failed to send message: {e}")
                    except Exception as e:
                        print(f"❌ Unexpected error: {e}")
                    producer.flush()

                    print(f"Inserted order and notified user: {email}")
                    consumer.commit()
                
                else:
                    print(f"Failed to insert order: {order_data}")
                                
            except Exception as e:
                print(f"Error processing order: {e}")

