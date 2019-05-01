# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import secrets
import pymongo
import json
import emoji
import pandas as pd
import os

app = dash.Dash(__name__)
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501
server = app.server


# initialization of mongodb connector
client = pymongo.MongoClient(secrets.mongodb)
db = client['mcd_dashboard']
mcd_emotions= db['mcd_emotion']
records = mcd_emotions.find().sort([('timestamp', -1)]).limit(150)
client.close()

#load unicode for emoji
emoji = pd.read_csv('./data/emoji_unicode.csv',names=['emoji','dummy'])

# data traces
traces = []
docs = []
i = 0
for doc in records:
    doc['id']= i
    i+=1
    docs.append(doc)
    trace = dict(
                type='scattermapbox',
                lat=[doc['coordinates'][1]],
                lon=[doc['coordinates'][0]],
                mode='markers',
                marker=dict(
                    size=8,
                    opacity=0.8,
                    color='#FF3333'

                ),
                hoverinfo='text',
                text=doc['id']
    )
    traces.append(trace)

# layout
layout = dict(
    autosize=True,
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    # plot_bgcolor="#191A1A",
    # paper_bgcolor="#020202",
    showlegend=False,
    title='Canada',
    mapbox=dict(
        accesstoken=secrets.mapbox,
        style="light",
        center=dict(
            lat=60,
            lon=-100
        ),
        zoom=2.2,
    )
)

tweets = []

for doc in docs[:6]:
    emoji_pics=["{}.png".format(i) for i in doc['emoji_indexes']]
    print(emoji_pics)
    tweets.append(
    html.Div(
    children=str(doc['id']+1)+"."+doc['tweet'],
    style={
        'textAlign': 'left'
    }))
    for emoji_pic in emoji_pics:
        tweets.append(
            html.Img(src=app.get_asset_url(emoji_pic),
            style={
                    'height': '6%',
                    'width': '6%'
                })
            )


app.layout = html.Div([
    html.Div(
                    [
                        dcc.Graph(id='main_graph',
                        figure={
                            'data':traces,
                            'layout':layout
                        })
                    ],
                    className='eight columns',
                    style={'margin-top': '20'}
),
 html.Div(
                    tweets,
                    className='four columns',
                    style={'margin-top': '20'}
),
])

if __name__ == "__main__":
    app.run_server(host='0.0.0.0',port=8888,debug=True)