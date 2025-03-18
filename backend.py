from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

# Create a Kafka producer
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

@app.route('/order', methods=['POST'])
def order():
    # Get data from the request
    data = request.json
    email = data.get('email')
    address = data.get('address')
    product = data.get('product')
    quantity = data.get('quantity')

    # Create a message to send to Kafka
    message = {
        'email': email,
        'address': address,
        'product': product,
        'quantity': quantity
    }

    # Send the message to the Kafka topic
    producer.send('ordertopic', message)
    producer.flush()  # Ensure the message is sent

    # Return a simple response message
    return jsonify({'message': 'In Queue , You will receive mail whether order is placed or not !'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)