from kafka import KafkaConsumer, KafkaProducer
import json
import time

ORDERDATA_TOPIC = "ordertopic"
INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

# STOCK = 3

KAFKA_BOOTSTRAP_SERVERS = "your-aiven-kafka-host:your-port"

SSL_CERT = "/path/to/service.cert" 
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

def process_order(order):

    with open("stock.json", "r") as file:
        data = json.load(file)

    STOCK = data["count"]

    orders = json.loads(order)
    email = orders["email"]
    product = orders["product"]
    quantity = int(orders["quantity"])

    if STOCK >= quantity:
        STOCK -= quantity 
        data["count"] = STOCK
        
        with open("stock.json", "w") as file:
            json.dump(data, file, indent=4)

        print(f"Order confirmed for {email}, Remaining stock: {STOCK}")
        future = producer.send(INSERT_TOPIC, orders)
        try:
            record_metadata = future.get(timeout=10)  # Wait for confirmation with a timeout
            print(f"✅ Message sent to {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
        except KafkaTimeoutError as e:
            print(f"❌ Failed to send message: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        producer.flush()
        print(STOCK)

    else:
        print(f"Order failed for {email}, product out of stock.")
        mail_data = {"email": email, "status": "Out of Stock"}
        future = producer.send(MAILS_TOPIC, mail_data)
        try:
            record_metadata = future.get(timeout=10)  # Wait for confirmation with a timeout
            print(f"✅ Message sent to {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
        except KafkaTimeoutError as e:
            print(f"❌ Failed to send message: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        producer.flush()

# consumer = KafkaConsumer(
#     ORDERDATA_TOPIC,
#     security_protocol="SSL",
#     ssl_cafile=SSL_CA,
#     ssl_certfile=SSL_CERT,
#     ssl_keyfile=SSL_KEY,
#     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
#     auto_offset_reset="earliest",
#     enable_auto_commit=False,
#     group_id="order-processor" 
# )
producer = KafkaProducer(bootstrap_servers='localhost:29092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))


consumer = KafkaConsumer(
    ORDERDATA_TOPIC,
    bootstrap_servers='localhost:29092',
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="order-processor" 
)

print("Order Processor is running...")

while True:
    try:
        print("polling msg")
        messages = consumer.poll(timeout_ms=2000)
        # print(messages)
        if not messages:
            continue  

        for message in messages.values(): 
            print("first loop")
            for record in message:
                print("Second loop")
                try:
                    order = json.dumps(record.value)
                    print(f"Received order: {order}")
                    process_order(order)
                    consumer.commit()
                except Exception as e:
                    print(f"Error : {e} ")
    
    except Exception as e:
        print(f"Error Polling mesaage : {e}")               






