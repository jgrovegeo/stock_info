import pandas as pd 
import datetime as dt
import tweepy as tw
import os
import json
import re
import plotly.express as px
import plotly as plotly
from configparser import ConfigParser
from pytz import timezone

# Variables that contains the credentials to access Twitter API
config = ConfigParser()
config.read('config.ini')
config.sections()

ACCESS_TOKEN = config['twitterAPI']['ACCESS_TOKEN']
ACCESS_SECRET = config['twitterAPI']['ACCESS_SECRET']
CONSUMER_KEY = config['twitterAPI']['CONSUMER_KEY']
CONSUMER_SECRET = config['twitterAPI']['CONSUMER_SECRET']

# Setup access to API
def connect_to_twitter_OAuth():
    auth = tw.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

    api = tw.API(auth, wait_on_rate_limit=True)
    return api

# Create API object
api = connect_to_twitter_OAuth()

# list of handles to check
# handle = ['PJ_Matlock', 'Hugh_Henne', 'MrZackMorris', 'The_Analyst_81', 'buysellshort', 'ACInvestorBlog', 'Anonymoustocks',
#             'notoriousalerts', 'beach_trades', 'Reformed_Trader', 'Mitch_Picks', 'RadioSilentplay', 'yatesinvesting']

# plots ticker mentions in a bar graph
def tickerPopularity(handles):    
    date_since = dt.datetime.now() # grabs todays date and replaces hours to midnight for comparision with twitter date results
    date_since = date_since.astimezone(timezone('US/Eastern')).replace(minute=0, hour=0, second=0, microsecond=0)
    print(str(date_since))
    print(type(date_since))
    
    
    data = []
    tweets_text = []
    twt_split = []

    # loops through handle list and grabs tickers
    for h in handles:
        tweets = tw.Cursor(api.user_timeline,
                        screen_name=h,
                        tweet_mode='extended',
                        include_retweets=False).items(50) # looks at 50 items for each handle
        # loops through each tweet per handle and appends them to a list
        
        for tweet in tweets:
            mined = {
                'handle': tweet.user.screen_name,
                'date': tweet.created_at,
                'tweet': tweet.full_text
            }
            twt_text = tweet.full_text
            # twt_date = tweet.created_at.replace(minute=0, hour=0, second=0, microsecond=0)
            twt_date = tweet.created_at
            twt_date = twt_date.astimezone(timezone('US/Eastern')).replace(minute=0, hour=0, second=0, microsecond=0)
            if str(twt_date) == str(date_since):
                data.append(mined)
                tweets_text.append(twt_text)
        # splits tweet strings 
        for ticker in tweets_text:
            split_txt = ticker.split(' ')
            for txt in split_txt:
                twt_split.append(txt)
    
    print(str(twt_date))
    print(type(twt_date))
    
    # runs list comprehension to find any list elements with '$' , indicating a ticker
    tickers = [t for t in twt_split if "$" in t]

    # further reduces and cleans ticker list
    cleaned_tickers = []
    for i in tickers:
        result = re.sub('([^a-zA-Z\s]+?)', "", i)
        if len(result) > 2 and len(result) < 5:
            result = result.replace('\n', "")
            cleaned_tickers.append(result.upper())

    # creates dataframe based on cleaned_ticker list
    df_tickers = pd.DataFrame(cleaned_tickers, columns=['ticker'])

    # counts the numbeter of tickers and makes new column count with values
    df_tickers = df_tickers['ticker'].value_counts().rename_axis('ticker').reset_index(name='count')

    print(df_tickers)
    
    influencers = 'Fintwit Influencers<br><br>@PJ_Matlock<br>@Hugh_Henne<br>@MrZackMorris<br>@The_Analyst_81<br>@buysellshort<br>@ACInvestorBlog<br>@Anonymoustocks<br>@notoriousalerts<br>@beach_trades<br>@Reformed_Trader<br>@Mitch_Picks<br>@RadioSilentplay<br>@yatesinvesting'
    # draws plotly histogram
    fig = px.histogram(df_tickers, 
                       y='count', 
                       x='ticker', 
                       height=650
                       )
    fig.update_layout({'plot_bgcolor': '#32383e',
                       'paper_bgcolor': '#272B30'},
                      font_color='#aaa',
                      font={'size':18},
                      title_text='Ticker mentions on Twitter for ' + str(dt.datetime.now(tz=timezone('US/Eastern')).strftime("%m/%d/%Y") + ' @ ' + dt.datetime.now(tz=timezone('US/Eastern')).strftime("%H:%M")) + ' (EST)', 
                      title_x=0.5,
                      title_y=.98,
                      annotations=[
                                {
                                    'x': .95,
                                    'y': .95,
                                    'text': influencers,
                                    'showarrow': False,
                                    'xref': 'paper',
                                    'yref': 'paper'
                                }]),
    fig.update_xaxes(showgrid=False, 
                     showline=True, 
                     linecolor='black',
                     linewidth=2, 
                     mirror=True, 
                     title_text='Tickers',
                     tickangle=45,
                     zeroline=False
                     )
    fig.update_yaxes(showgrid=False, 
                     showline=True,
                     linecolor='black',
                     linewidth=2, 
                     mirror=True, 
                     title_text='Mentions',
                     zeroline=False
                     )
    fig.update_traces(marker_color='#aaa')
    # plot = fig.show()
    plot_div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
    
    return plot_div, cleaned_tickers

# tickerPopularity(handle)