import pika, sys, os
import json
import uuid 

def main():
    
    def on_message_received(ch, method, props, body):
        data = json.loads(body)
        print(f"Received response: {data}")
        
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    reply_queue = channel.queue_declare(queue='', exclusive=True)
    
    channel.basic_consume(queue=reply_queue.method.queue, auto_ack=True, on_message_callback=on_message_received)
    
    channel.queue_declare(queue='request-queue')
    
    cor_id = str(uuid.uuid4())
    print(f'Sending Request: {cor_id}')

    example_body = {'brand': 'La Sportiva', 'closure': 'Slipper', 'type': 'Sport Climbing'}

    channel.basic_publish('', routing_key='request-queue', properties=pika.BasicProperties(reply_to=reply_queue.method.queue, correlation_id = cor_id), body=json.dumps(example_body))
    print("Starting Client")
    
    channel.start_consuming()
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            