from kafka import KafkaConsumer, KafkaProducer
import json
import time

ORDERDATA_TOPIC = "orderdata"
INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

STOCK = 20  

KAFKA_BOOTSTRAP_SERVERS = "your-aiven-kafka-host:your-port"

SSL_CERT = "/path/to/service.cert" 
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    security_protocol="SSL",
    ssl_cafile=SSL_CA,
    ssl_certfile=SSL_CERT,
    ssl_keyfile=SSL_KEY,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_order(order):
    global STOCK 
    email = order["email"]
    product = order["product"]
    quantity = order["quantity"]

    if STOCK >= quantity:
        STOCK -= quantity 
        print(f"Order confirmed for {email}, Remaining stock: {STOCK}")
        producer.send(INSERT_TOPIC, value=order)
        producer.flush()

    else:
        print(f"Order failed for {email}, product out of stock.")
        mail_data = {"email": email, "status": "Out of Stock"}
        producer.send(MAILS_TOPIC, value=mail_data)
        producer.flush()

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

while True:
    messages = consumer.poll(timeout_ms=1000)
    if not messages:
        continue  

    for message in messages.values(): 
        for record in message:
            try:
                order = json.loads(record.value)
                print(f"Received order: {order}")
                process_order(order)
                consumer.commit()
                






