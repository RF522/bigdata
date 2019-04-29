# coding=utf-8

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import secrets
import json

access_token = secrets.access_token
access_token_secret = secrets.access_secret_token

consumer_key = secrets.consumer_key
consumer_secret = secrets.consumer_secret_key

# streamming listener
class StdOutListener(StreamListener):
    def on_data(self, data):
       
        json_string = json.loads(data)
        if json_string.get('place',{}).get('country') == 'Canada':

            producer.send_messages('canada', json.dumps(json_string, ensure_ascii=False).encode('utf-8'))
            
        return True
    def on_err(self, status):
        print(status)

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

stream = Stream(auth, l)
# stream filter based on canada
stream.filter(locations=[ -132.678892, 38.254429,-50.950142,62.091894])
