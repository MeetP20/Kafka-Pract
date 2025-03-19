from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json
import credential
from flask_cors import CORS
from kafka import KafkaAdminClient

KAFKA_BOOTSTRAP_SERVERS = credential.kafka_service_uri  

SSL_CERT = "/path/to/service.cert"  
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

# producer = KafkaProducer(
#     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#     security_protocol="SSL",
#     ssl_cafile=SSL_CA,
#     ssl_certfile=SSL_CERT,
#     ssl_keyfile=SSL_KEY,
#     value_serializer=lambda v: json.dumps(v).encode('utf-8')
# )
producer = KafkaProducer(bootstrap_servers='localhost:29092',value_serializer=lambda v: json.dumps(v).encode('utf-8'))

app = Flask(__name__)
CORS(app, resources={r"/order": {"origins": "*"}})
@app.route('/order', methods=['POST'])
def order():
    print("api called")
    data = request.json
    email = data.get('email')
    address = data.get('address')
    product = data.get('product')
    quantity = data.get('quantity')

    message = {
        'email': email,
        'address': address,
        'product': product,
        'quantity': quantity
    }

    print(message) 
    future = producer.send('ordertopic', message)
    try:
        record_metadata = future.get(timeout=10)  # Wait for confirmation with a timeout
        print(f"✅ Message sent to {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
        return "In Queue, You will receive an email whether the order is placed or not!" , 200
    except KafkaTimeoutError as e:
        print(f"❌ Failed to send message: {e}")
        return "Failed to place order. Please try again later.", 500
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return "An unexpected error occurred.", 500

    producer.flush()

if __name__ == '__main__':
    app.run(debug=True, port=5000)