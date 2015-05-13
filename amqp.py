import pika
import settings

def publish(resource, data):
    credentials = pika.PlainCredentials('test', 'test')
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.brokerHost, 5672, 'cloud4rpi', credentials))

    channel = connection.channel()
    channel.queue_declare(queue='devices')

    channel.basic_publish(exchange='', routing_key=resource, body=data)

    connection.close()
