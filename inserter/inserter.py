from kafka import KafkaConsumer, KafkaProducer
import psycopg2
import json

INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

DB_CONFIG = {
    "dbname": "kafka",
    "user": "admin",
    "password": "root",
    "host": "postgres",
    "port": 5432
}

producer = KafkaProducer(bootstrap_servers='kafka1:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))


consumer = KafkaConsumer(
    INSERT_TOPIC,
    bootstrap_servers='kafka1:9092',
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="inserter" 
)

def insert_order(order_data):
    try:
        order_data = json.loads(order_data)
        email = order_data["email"]
        product = order_data["product"]
        address = order_data["address"]
        quantity = int(order_data["quantity"])

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = "INSERT INTO kafka (email, address, product, quantity) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (email, address, product, quantity))
        conn.commit()
        cur.close()
        conn.close()
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

                    print(f"Inserted order and will notify user {email} via mail")
                    consumer.commit()
                
                else:
                    print(f"Failed to insert order: {order_data}")
                                
            except Exception as e:
                print(f"Error processing order: {e}")

