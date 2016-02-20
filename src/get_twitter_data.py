from utilities import *
from TwitterSearch import *
import openpyxl as xl
from datetime import datetime
import datetime as dt
from dateutil import tz
import json


def setupthesheet():
    wb = xl.load_workbook(filename=config.get('filepath'))
    sheet = wb.get_sheet_by_name(config.get('sheet'))
    sheet._get_cell(1, 1).value = 'User Handle'
    sheet._get_cell(1, 2).value = 'Tweet'
    sheet._get_cell(1, 3).value = 'ReTweet Count'
    sheet._get_cell(1, 4).value = 'In Reply To'
    sheet._get_cell(1, 5).value = 'Created At'
    sheet._get_cell(1, 6).value = 'ID'
    sheet._get_cell(1, 7).value = 'Place'
    sheet._get_cell(1, 8).value = 'Language'
    return sheet, wb


# need to add the ability to search multiple keywords.
# need to have the ability to store the csv in a seperate location with the timestamp of the running

# Also give a wayto print out the dates that are used..

def convertTime(time):
    from_zone = tz.gettz('GMT')
    to_zone = tz.gettz('Singapore')
    utc = datetime.strptime(time, '%a %b %d %H:%M:%S +0000 %Y')
    utc = utc.replace(tzinfo=from_zone)
    newtime = str(utc.astimezone(to_zone))[:19]
    return newtime

def saveTweets(keyword):
    sheet, wb = setupthesheet()
    keyword_list = list()
    keyword_list.append(keyword)
    # try:
    #     tweets = searchTwitter(keyword_list)
    # except TwitterSearchException as e:
    #     print(e)
    row = 2
    # print('here')
    tso = TwitterSearchOrder()
    tws = TwitterSearch(
            consumer_key=config.get('consumer_key'),
            consumer_secret=config.get('consumer_secret'),
            access_token=config.get('access_token'),
            access_token_secret=config.get('access_token_secret')
    )
    tso.set_keywords(keyword_list, or_operator=True)
    tso.set_language('en')
    for i in range(11,21):
        filename = config.get('filepath') + '_'+ str(i)
        tso.set_until(dt.date(2016,02,i))
        for tweet in tws.search_tweets_iterable(tso):
            # f = open('/Users/gautamborgohain/Desktop/dump.txt','a')
            # f.write(tweet)
            # f.clos
            with open('/Users/gautamborgohain/Desktop/dump.json', 'a') as f:
                json.dump(tweet, f)
            sheet._get_cell(row, 1).value = tweet['user']['screen_name']  # user handle
            sheet._get_cell(row, 2).value = tweet['text']  # tweet
            sheet._get_cell(row, 3).value = tweet['retweet_count']  # retweet count
            sheet._get_cell(row, 4).value = tweet['in_reply_to_screen_name']  # reply to?
            sheet._get_cell(row, 5).value = convertTime(tweet['created_at'])  # created_at
            sheet._get_cell(row, 6).value = tweet['id_str']  # id_str
            if tweet['place'] is not None:
                sheet._get_cell(row, 7).value = tweet['place']['full_name']  # Place
            sheet._get_cell(row, 8).value = tweet['user']['lang']  # lang
            row += 1

        wb.save(filename=filename)
    # f.close()
    print('Finished')


saveTweets('SMRT_Singapore')