import re
from utilities import *
import pandas
import openpyxl as xl
from nltk.corpus import stopwords

class process_tweets:

    config = getConfigs()
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
        #tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
        #trim
        tweet = tweet.strip('\'"')

        return tweet

    def replaceTwoOrMore(self,tweet):
        #look for 2 or more repetitions of character and replace with the character itself
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        return pattern.sub(r"\1\1", tweet)

    def removeStopWords(self,tokens):
        stopwordsList = stopwords.words('english')
        stopwordsList.append('AT_USER')
        stopwordsList.append('URL')
        stopwordsList.append('at_user')
        stopwordsList.append('url')
        filtered_tokens= [word for word in tokens if word not in stopwordsList]
        return filtered_tokens

    def writeUpdatedTweets(self,tweetsdf):
            wb = xl.load_workbook(filename=self.config.get('filepath'))
            sheet = wb.get_sheet_by_name(self.config.get('sheet2'))
            sheet._get_cell(1,1).value = 'User Handle'
            sheet._get_cell(1,2).value = 'Tweet'
            sheet._get_cell(1,3).value = 'Retweet count'
            sheet._get_cell(1,4).value = 'In Reply To'
            sheet._get_cell(1,5).value = 'Created At'
            sheet._get_cell(1,6).value = 'ID'
            sheet._get_cell(1,7).value= 'Place'
            sheet._get_cell(1,8).value = 'Language'
            i = 2
            for t in range(1,len(tweetsdf)):
                tweet = tweetsdf.get_value(t,'Tweet')
                if tweet != " ":
                    sheet._get_cell(i,1).value = tweetsdf.get_value(t,'User Handle')#user handle
                    sheet._get_cell(i,2).value = tweetsdf.get_value(t,'Tweet')
                    sheet._get_cell(i,3).value = tweetsdf.get_value(t,'ReTweet Count')
                    sheet._get_cell(i,4).value = tweetsdf.get_value(t,'In Reply To')
                    sheet._get_cell(i,5).value = tweetsdf.get_value(t,'Created At')
                    sheet._get_cell(i,6).value = tweetsdf.get_value(t,'ID')
                    sheet._get_cell(i,7).value = tweetsdf.get_value(t,'Place')
                    sheet._get_cell(i,8).value = tweetsdf.get_value(t,'Language')
                    i+=1
            wb.save(filename=self.config.get('filepath'))

    #This function is removing the unwanted tweets and returning the cleaned DF
    def removeBadTweets(self,tweetsdf):
        newDF = pandas.DataFrame(columns=tweetsdf.columns)
        baddatacount = 1
        for i in range(1,len(tweetsdf)):
            tweet = tweetsdf.get_value(i,'Tweet')
            tweet = self.regex_stuff(tweet) # remove using the regex function
            tweet = tweet.encode('ascii', 'ignore').decode('ascii')  #remove the weird characters
            if tweet.startswith('I\'m at ') or tweet.startswith('i\'m at '):
                baddatacount +=1
            else:
                tweetsdf = tweetsdf.set_value(i,'Tweet',tweet)
                newDF = newDF.append(tweetsdf[i:i+1])
                #print(tweetsdf.ix[i])

        print("Completed, Bad count = ", baddatacount)
        print(newDF.head())

        return newDF

    def runPreProcessing(self,tweetsdf):
        wb = xl.load_workbook(filename=self.config.get('filepath'))
        sheet = wb.get_sheet_by_name(self.config.get('sheet'))
        row = 2
        for tweet in tweetsdf['Tweet']:
            tweet = self.regex_stuff(tweet)
            sheet._get_cell(row,9).value = tweet
            row +=1
        wb.save(filename=self.config.get('filepath'))

