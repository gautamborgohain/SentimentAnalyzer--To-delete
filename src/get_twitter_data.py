from utilities import *
from TwitterSearch import *
import openpyxl as xl
import datetime

class TwitterData:

    config = getConfigs('c')
    def searchTwitter(self,keyword):
        tso = TwitterSearchOrder()

        ts = TwitterSearch(
            consumer_key=self.config.get('consumer_key'),
            consumer_secret=self.config.get('consumer_secret'),
            access_token = self.config.get('access_token'),
            access_token_secret = self.config.get('access_token_secret')
        )
        tso.set_keywords(keyword)
        tso.set_language('en')
        tso.set_until(datetime.date(2016,1,1))
        tweets = ts.search_tweets_iterable(tso)
        return tweets

    def setupthesheet(self):
        wb = xl.load_workbook(filename=self.config.get('filepath'))
        sheet = wb.get_sheet_by_name(self.config.get('sheet'))
        sheet._get_cell(1,1).value = 'User Handle'
        sheet._get_cell(1,2).value = 'Tweet'
        sheet._get_cell(1,3).value = 'ReTweeted'
        sheet._get_cell(1,4).value = 'In Reply To'
        sheet._get_cell(1,5).value = 'Created At'
        sheet._get_cell(1,6).value = 'Retweet count'
        sheet._get_cell(1,7).value= 'Place'
        sheet._get_cell(1,8).value = 'Language'
        return sheet,wb

    def saveTweets(self,keyword):
        sheet,wb = self.setupthesheet()
        keyword_list = list()
        keyword_list.append(keyword)
        try:
            tweets = self.searchTwitter(keyword_list)
        except TwitterSearchException as e:
            print(e)
        row = 2
        print('here')
        for tweet in tweets:
            sheet._get_cell(row,1).value = tweet['user']['screen_name']#user handle
            sheet._get_cell(row,2).value = tweet['text']#tweet
            sheet._get_cell(row,3).value = tweet['retweeted']#retweet?
            sheet._get_cell(row,4).value = tweet['in_reply_to_screen_name']#reply to?
            #sheet._get_cell(row,5).value = tweet['created_at']#created_at
            #sheet._get_cell(row,6).value = tweet['retweet_count']#retweet_count
            #sheet._get_cell(row,6).value = tweet['place']#Place
            sheet._get_cell(row,8).value = tweet['lang']#lang
            row +=1

        wb.save(filename=self.config.get('filepath'))
        print('Finished')
