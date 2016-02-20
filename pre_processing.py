import re
import pandas
import openpyxl as xl

from openpyxl import Workbook


path = '/Users/gautamborgohain/Desktop/data_cleaned.xlsx'




def replaceTwoOrMore(tweet):
    # look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", tweet)





def writeUpdatedTweets(tweetsdf):
    wb = xl.load_workbook(filename=path)
    sheet = wb.get_sheet_by_name('data2')
    sheet._get_cell(1, 1).value = 'User Handle'
    sheet._get_cell(1, 2).value = 'Tweet'
    sheet._get_cell(1, 3).value = 'Retweet count'
    sheet._get_cell(1, 4).value = 'In Reply To'
    sheet._get_cell(1, 5).value = 'Created At'
    sheet._get_cell(1, 6).value = 'ID'
    sheet._get_cell(1, 7).value = 'Place'
    sheet._get_cell(1, 8).value = 'Language'
    i = 2
    for t in range(1, len(tweetsdf)):
        tweet = tweetsdf.get_value(t, 'Tweet')
        if tweet != " ":
            sheet._get_cell(i, 1).value = tweetsdf.get_value(t, 'User Handle')  # user handle
            sheet._get_cell(i, 2).value = tweetsdf.get_value(t, 'Tweet')
            sheet._get_cell(i, 3).value = tweetsdf.get_value(t, 'ReTweet Count')
            sheet._get_cell(i, 4).value = tweetsdf.get_value(t, 'In Reply To')
            sheet._get_cell(i, 5).value = tweetsdf.get_value(t, 'Created At')
            sheet._get_cell(i, 6).value = tweetsdf.get_value(t, 'ID')
            sheet._get_cell(i, 7).value = tweetsdf.get_value(t, 'Place')
            sheet._get_cell(i, 8).value = tweetsdf.get_value(t, 'Language')
            i += 1
    wb.save(filename=path)




def runPreProcessing(tweetsdf):
    wb = Workbook()
    sheet1 = wb.active
    sheet1.title = "cleaned data"
    newDF = pandas.DataFrame(columns=tweetsdf.columns)
    for row in range(1,len(tweetsdf)):
        tweet = regex_stuff(tweetsdf.get_value(row, 'Tweet'))
        # sheet1.append(tweetdata)
        # newDF.append(tweetdata)
    wb.save(filename=path)



# This function is removing the unwanted tweets and returning the cleaned DF
