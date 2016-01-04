import re
from utilities import *
import pandas
import openpyxl as xl

class process_tweets:

    config = getConfigs('c')
    def regex_stuff(self,tweet):
        #Convert to lower case
        tweet = tweet.lower()
        #Convert www.* or https?://* to URL
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
        #Convert @username to AT_USER
        tweet = re.sub('@[^\s]+','AT_USER',tweet)
        #Remove additional white spaces
        tweet = re.sub('[\s]+', ' ', tweet)
        #Replace #word with word
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        #trim
        tweet = tweet.strip('\'"')

        return tweet

    def writeUpdatedTweets(self,tweetsdf):
            wb = xl.load_workbook(filename=self.config.get('filepath'))
            sheet = wb.get_sheet_by_name(self.config.get('sheet2'))
            sheet._get_cell(1,1).value = 'User Handle'
            sheet._get_cell(1,2).value = 'Tweet'
            sheet._get_cell(1,3).value = 'ReTweeted'
            sheet._get_cell(1,4).value = 'In Reply To'
            sheet._get_cell(1,5).value = 'Created At'
            sheet._get_cell(1,6).value = 'Retweet count'
            sheet._get_cell(1,7).value= 'Place'
            sheet._get_cell(1,8).value = 'Language'
            i = 2
            for t in range(1,len(tweetsdf)):
                tweet = tweetsdf.get_value(t,'Tweet')
                if tweet != " ":
                    sheet._get_cell(i,1).value = tweetsdf.get_value(t,'User Handle')#user handle
                    sheet._get_cell(i,2).value = tweetsdf.get_value(t,'Tweet')
                    sheet._get_cell(i,3).value = tweetsdf.get_value(t,'ReTweeted')
                    sheet._get_cell(i,4).value = tweetsdf.get_value(t,'In Reply To')
                    #sheet._get_cell(row,5).value = tweet['created_at']#created_at
                    #sheet._get_cell(row,6).value = tweet['retweet_count']#retweet_count
                    #sheet._get_cell(row,6).value = tweet['place']#Place
                    #sheet._get_cell(i,8).value = tweetsdf.get_value(t,'Language')
                    i+=1
            wb.save(filename=self.config.get('filepath'))

    def removeBadTweets(self,tweetsdf):
        for i in range(1,len(tweetsdf)):
            tweet = tweetsdf.get_value(i,'Tweet')
            tweet = self.regex_stuff(tweet)
            if tweet.startswith('I\'m at ') or tweet.startswith('i\'m at '):
                tweet = " "
            tweetsdf = tweetsdf.set_value(i,'Tweet',tweet)


        return tweetsdf

    def runPreProcessing(self,tweetsdf):
        wb = xl.load_workbook(filename=self.config.get('filepath'))
        sheet = wb.get_sheet_by_name(self.config.get('sheet'))
        row = 2
        for tweet in tweetsdf['Tweet']:
            tweet = self.regex_stuff(tweet)
            sheet._get_cell(row,9).value = tweet
            row +=1
        wb.save(filename=self.config.get('filepath'))

