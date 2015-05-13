import pika
import json
import settings

def publish(data):

    credentials = pika.PlainCredentials(settings.brokerUser, settings.brokerPass)
    parameters = pika.ConnectionParameters(settings.brokerHost,
                                           settings.brokerPort,
                                           settings.brokerVirtualHost,
                                           credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue=settings.brokerQueue, durable=True)
    print data

    channel.basic_publish(exchange='', routing_key=settings.brokerQueue, body=json.dumps(data))
    connection.close()
