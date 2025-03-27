from kafka import KafkaConsumer, KafkaProducer
import smtplib
import json
import os
from dotenv import load_dotenv, dotenv_values 

MAILS_TOPIC = "mails"

consumer = KafkaConsumer(
    MAILS_TOPIC,
    bootstrap_servers='kafka1:9092',
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    group_id="mailer"
)

def send_mail(email, msg):
    try:
        load_dotenv()
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'prajapatimeet301@gmail.com'
        smtp_password =  os.getenv("email_password")

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
