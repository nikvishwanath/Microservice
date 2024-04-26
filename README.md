# Microservice

To request data from the microservice, send a JSON object with the request parameters in the body of the request.  In the below example, the connection and queues are initiated, then the example_body is passed into the body of the request: 
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    reply_queue = channel.queue_declare(queue='', exclusive=True)
    
    channel.basic_consume(queue=reply_queue.method.queue, auto_ack=True, on_message_callback=on_message_received)
    
    channel.queue_declare(queue='request-queue')
    
    cor_id = str(uuid.uuid4())
    print(f'Sending Request: {cor_id}')
    
    example_body = {'brand': 'La Sportiva', 'closure': 'Lace', 'type': 'Sport Climbing'}

    channel.basic_publish('', routing_key='request-queue', properties=pika.BasicProperties(reply_to=reply_queue.method.queue, correlation_id = cor_id), body=json.dumps(example_body))


To receive data from the microservice, call the on_message_received method when a message is consumed.  

    def on_message_received(ch, method, props, body):
        data = json.loads(body)
        print(f"Received response: {data}")
    
    channel.basic_consume(queue=reply_queue.method.queue, auto_ack=True, on_message_callback=on_message_received)


Below is a sequence diagram that shoes how requesting and receiving data work.  

<img src="/ULM sequence diagram.jpg" alt="Alt text" title="Optional title">
