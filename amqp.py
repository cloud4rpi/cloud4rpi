import pika
import json
import settings

def publish(resource, data):

    credentials = pika.PlainCredentials('test', 'test')
    parameters = pika.ConnectionParameters(settings.brokerHost,
                                           5672,
                                           'cloud4rpi',
                                           credentials)
    #parameters = pika.URLParameters('amqp://test:test@172.22.2.150:5672/cloud4rpi')

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    #channel.queue_declare(queue='device_queue', durable=True)


    print '==== publish data ===='
    print resource, data

    channel.basic_publish(exchange='', routing_key='device_queue', body=json.dumps(data))

    connection.close()
