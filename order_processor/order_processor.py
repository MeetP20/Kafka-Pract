from kafka import KafkaConsumer, KafkaProducer
import json
import time

ORDERDATA_TOPIC = "ordertopic"
INSERT_TOPIC = "insert"
MAILS_TOPIC = "mails"

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

producer = KafkaProducer(bootstrap_servers='kafka1:9092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))


consumer = KafkaConsumer(
    ORDERDATA_TOPIC,
    bootstrap_servers='kafka1:9092',
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






