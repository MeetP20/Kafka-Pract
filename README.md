# Kafka-Based Order Processing System

This is a microservices-based order processing system using **Kafka, Flask, PostgreSQL, and Docker Compose**. It simulates an e-commerce ordering system where orders are processed through Kafka and stored in a database.

## Architecture
- **Backend Service** (`backend.py`): Accepts order requests and publishes them to Kafka.
- **Order Processor** (`order_processor.py`): Reads orders from Kafka, updates stock, and forwards messages.
- **Inserter Service** (`inserter.py`): Inserts processed orders into PostgreSQL.
- **Mailer Service** (`mailer.py`): Sends email notifications for order status.
- **Kafka & Zookeeper**: Handles event streaming between services.
- **PostgreSQL**: Stores order and stock data.
- **Kafka UI**: Provides a web-based UI to monitor Kafka topics.

---

## Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/MeetP20/Kafka-Pract.git
cd Kafka-Pract
```

### 2️⃣ Start Services using Docker Compose
```bash
docker-compose --build
```
```bash
docker-compose up -d
```

### 3️⃣ Create Kafka Topics (Manually)
Since topics are not pre-initialized, run the following command inside the Kafka container:
```bash
docker exec -it <kafka-container-id> kafka-topics.sh --create --topic ordertopic --bootstrap-server kafka1:9092 --partitions 1 --replication-factor 1
docker exec -it <kafka-container-id> kafka-topics.sh --create --topic insert --bootstrap-server kafka1:9092 --partitions 1 --replication-factor 1
docker exec -it <kafka-container-id> kafka-topics.sh --create --topic mails --bootstrap-server kafka1:9092 --partitions 1 --replication-factor 1
```
Alternatively, you can use **Kafka UI** at `http://localhost:8080` to create topics.

### 4️⃣ Verify Running Services
```bash
docker ps
```

---

## API Usage

### Place an Order
- Endpoint: `POST http://localhost:5000/order`
- Request Body:
```json
{
  "email": "user@example.com",
  "address": "123 Main St",
  "product": "Laptop",
  "quantity": 1
}
```
- Expected Response:
```json
"In Queue, You will receive an email whether the order is placed or not!"
```

---

## Troubleshooting

1. **Kafka "NoBrokersAvailable" Error?**
   - Ensure Kafka is running: `docker logs kafka1`
   - Restart Kafka: `docker-compose restart kafka1`

2. **"Failed to fetch" Error on Frontend?**
   - Check if the backend service is running:
     ```bash
     docker logs backend
     ```
   - Make sure CORS is enabled in `backend.py`.

3. **Mounting Errors for `stock.json`?**
   - Ensure the `stock.json` file exists in the correct directory before running `docker-compose`.
   - Use **absolute path** in `docker-compose.yml`:
     ```yaml
     volumes:
       - ./stock.json:/app/stock.json
     ```

---

## Future Enhancements
- Automate topic creation in `docker-compose.yml`.
- Implement authentication & logging.
- Deploy to AWS ECS/Fargate with Terraform.

---

🚀 **Contributions & Issues**
Feel free to open issues or submit PRs. Happy coding! 🎯

