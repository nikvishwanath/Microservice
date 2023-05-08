from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
import pika, sys, os

def main():
    
    def retrieve_shoes(brand, closure=None, type=None):
        return_object = {}
        request = HTMLSession()
        url = "https://www.backcountry.com/climbing-shoes"
        
        # Brand
        if brand == "La Sportiva":
            filtered_url = url + "?p=Brand%3A120"
        elif brand == "Scarpa":
            filtered_url = url + "?p=Brand%3A100000327"
        elif brand == "Evolv":
            filtered_url = url + "?p=Brand%3A100000486"
        elif brand == "Butora":
            filtered_url = url + '?p=Brand%3A100005426'
        elif brand == "Ocurn":
            filtered_url = url + '?p=Brand%3A100006562' 
        elif brand == "Black Diamond":
            filtered_url = url + '?p=Brand%3A14'  
        elif brand == "Boreal":
            filtered_url = url + '?p=Brand%3A100005376'  
        elif brand == "Five Ten":
            filtered_url = url + '?p=Brand%3A100000092' 
        elif brand == "Lowa":
            filtered_url = url + '?p=Brand%3A188' 
        elif brand == "Mad Rock":
            filtered_url = url + '?p=Brand%3A100000453'  
        elif brand == "Red Chili":
            filtered_url = url + '?p=Brand%3A100004338'
        elif brand == "So Ill Holds":
            filtered_url = url + '?p=Brand%3A100001034'
        elif brand == "Tenaya":
            filtered_url = url + '?p=Brand%3A100001600'   
        elif brand == "UnParallel":
            filtered_url = url + '?p=Brand%3A200004775'  
        else:
            return_object = {"Error": "Brand Not Found"}
            final_return_object = json.dumps(return_object)
            return final_return_object
        
        # Closure
        if closure is None: 
            new_url = filtered_url
        elif closure == 'Hook-And-Loop':
            new_url = filtered_url + '%7CClosure%3AHook-and-Loop'
        elif closure == 'Lace':
            new_url = filtered_url + '%7CClosure%3ALace' 
        elif closure == 'Slipper':
            new_url = filtered_url + '%7CClosure%3ASlipper'
        else:
            return_object = {"Error": "Closure Not Found"}
            final_return_object = json.dumps(return_object)
            return final_return_object
        # Type
        if type is None:
            final_url = new_url
        elif type == 'Sport Climbing':
            final_url = new_url + '%7CRecommended+Use%3ASport+Climbing'
        elif type == 'Bouldering':
            final_url = new_url + '%7CRecommended+Use%3ABouldering'
        elif type == 'Climbing Training':
            final_url = new_url + '%7CRecommended+Use%3AClimbing+Training'
        elif type == 'Trad Climbing':
            final_url = new_url + '%7CRecommended+Use%3ATrad+Climbing'
        else:
            return_object = {"Error": "Type Not Found"}
            final_return_object = json.dumps(return_object)
            return final_return_object

        response = request.get(final_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # All shoe names matching request.  
        shoe_name = soup.find_all("h2", attrs={'class': 'chakra-heading css-1gfqank'})
        shoe_names = []
        for shoe in shoe_name:
            shoe_names.append(shoe.text)
            return_object[shoe.text] = {}
        
        # Links to the individual shoes. 
        shoe_links = []
        a_tag = soup.find_all('a', {'class': 'chakra-linkbox__overlay css-1uw88nq'})
        for a in a_tag:
            shoe_links.append('https://backcountry.com' + a['href'] + '#product-info-tabs')
        
        # Consolodating the information for the response. 
        shoe_counter = 0
        for link in shoe_links:
            new_response = request.get(link)
            soup = BeautifulSoup(new_response.text, 'html.parser')
            tech_specs = soup.find_all("dd", {"class": "chakra-text css-1x5aigl"})
            description = soup.find("div", {"class": "css-1h9bni0"})
            specs_list = []
            for i in tech_specs:
                specs_list.append(i.text)
            return_object[shoe_names[shoe_counter]]["Description"] = description.text
            return_object[shoe_names[shoe_counter]]["Upper Material"] = specs_list[0]
            return_object[shoe_names[shoe_counter]]["Lining"] = specs_list[1]
            return_object[shoe_names[shoe_counter]]["Closure"] = specs_list[2]
            shoe_counter += 1
        
        # Return JSON object. 
        final_return_object = {brand: return_object}
        last_return = json.dumps(final_return_object)
        
        return last_return
    
    def on_request(ch, method, properties, body):
        print(" [x] Received %r" % body)
        deserialized_body = json.loads(body)
        ch.basic_publish('', routing_key=properties.reply_to, body=retrieve_shoes((deserialized_body['brand']), deserialized_body['closure'], deserialized_body['type']))
        print("Sent the response")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel() 

    channel.queue_declare(queue='request-queue')
    channel.basic_consume(queue='request-queue', auto_ack=True, on_message_callback=on_request)

    print(' [*] Waiting for messages. To exit press CTRL+C')
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