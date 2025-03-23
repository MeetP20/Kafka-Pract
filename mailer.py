from kafka import KafkaConsumer, KafkaProducer
import smtplib
import json
import credential

KAFKA_BOOTSTRAP_SERVERS = credential.kafka_service_uri  

SSL_CERT = "/path/to/service.cert"  
SSL_KEY = "/path/to/service.key"
SSL_CA = "/path/to/ca.pem"

MAILS_TOPIC = "mails"

# consumer = KafkaConsumer(
#     MAILS_TOPIC,
#     bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
#     security_protocol="SSL",
#     ssl_cafile=SSL_CA,
#     ssl_certfile=SSL_CERT,
#     ssl_keyfile=SSL_KEY,
#     value_deserializer=lambda m: json.loads(m.decode("utf-8")),
#     auto_offset_reset="earliest",
#     enable_auto_commit=True,
#     group_id="mailer"
# )

consumer = KafkaConsumer(
    MAILS_TOPIC,
    bootstrap_servers='localhost:29092',
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="mailer"
)

def send_mail(email, msg):
    try:

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'prajapatimeet301@gmail.com'
        smtp_password = credential.email_password

        from_email = 'prajapatimeet301@gmail.com'
        subject = 'Status of Order'

        message = f'Subject: {subject}\n\n{msg}'

        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_username, smtp_password)
            smtp.sendmail(from_email, email, message)
        return True

    except Exception as e:
        print(f"Error sending mail: {e}")
        return False

print("Mailer Microservice is running...")

while True:
    messages = consumer.poll(timeout_ms=1000)

    if not messages:  
        continue  

    for message in messages.values():
        for record in message:
            try:
                
                mail_value = json.dumps(record.value)
                mail_data = json.loads(mail_value)

                email = mail_data["email"]
                msg = mail_data["status"]
                
                if send_mail(email, msg):
                    print(f"Email sent and notified user: {email}")
                    consumer.commit()
                
                else:
                    print(f"Failed to send mail to user: {email}")
                                
            except Exception as e:
                print(f"Error Mailing User: {e}")
