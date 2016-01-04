import pandas
import get_twitter_data as gtd
import pre_processing as pre_pros
from utilities import *

class controller:
    config = getConfigs('c')
    fetchednewData = False
    tweetsdf = pandas.DataFrame()
    def triggetTwitterCapture(self,keyword):
        try:
            td = gtd.TwitterData()
            td.saveTweets(keyword)
            self.fetchednewData = True
        except Exception as e:
            print('Error in get_twitter_data py. Exception : %s' %e)

    def getData(self,fetchNewData = False,sheet = "sheet"):
        filepath = self.config.get('filepath')
        sheet = self.config.get(sheet)
        if fetchNewData == True:
            self.triggetTwitterCapture()
            if self.fetchedData == True:
               frame = pandas.read_excel(filepath,sheet)
            else:
                frame = pandas.read_excel(filepath,sheet)#read the same file nonetheless for now
                print('Updated Twitter file was not read')
        else:
            frame = pandas.read_excel(filepath,sheet)#read the same file nonetheless for now
            print('Old Twitter Data file was read')
        self.tweetsdf = frame
        return frame

    def triggerPreProcessing(self):
        pp = pre_pros.process_tweets()
        pp.runPreProcessing(self.tweetsdf)
        print('Preprocessing complete')

#set fetchNewData as True if you want to pull twitter data again