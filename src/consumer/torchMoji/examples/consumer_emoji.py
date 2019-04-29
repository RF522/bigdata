# -*- coding: utf-8 -*-
from kafka import KafkaConsumer
from json import loads
import secrets
import pymongo

import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import json
import numpy as np

from torchmoji.sentence_tokenizer import SentenceTokenizer
from torchmoji.model_def import torchmoji_emojis
from torchmoji.global_variables import PRETRAINED_PATH, VOCAB_PATH

# load deepMoji load
maxlen = 140

print('Tokenizing using dictionary from {}'.format(VOCAB_PATH))
with open(VOCAB_PATH, 'r') as f:
    vocabulary = json.load(f)

st = SentenceTokenizer(vocabulary, maxlen)

print('Loading model from {}.'.format(PRETRAINED_PATH))
model = torchmoji_emojis(PRETRAINED_PATH)
print(model)

# initialization of mongo client
client = pymongo.MongoClient(secrets.mongodb)
db = client['mcd_dashboard']
mcd_emotions= db['mcd_emotion']



# Initialization of Kafka consumer
consumer = KafkaConsumer(
    'canada',
     bootstrap_servers=['172.18.0.2:9092'],
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: loads(x.decode('utf-8')))

# streaming tweet to deepMoji model
for message in consumer:
    print('reciving message')
    message = message.value
    text = message[u'text']
    print(message['place'])
    tokenized, _, _ = st.tokenize_sentences([text])
    prob = model(tokenized)[0]
    coordinates = np.mean(message['place']['bounding_box']['coordinates'][0], axis=0)
    print(coordinates)
    indexes = prob.argsort()[-5:][::-1]
    record_data = {
        'tweet':text,
        'emoji_indexes':list(indexes),
        'coordinates':list(coordinates)
    }

    mcd_emotions.insert_one(record_data)

# mongodb connection close
client.close()