import pandas
import matplotlib.pyplot as plt
from datetime import datetime

def preparePlottingFrame(dataFrame,trainingFrame):
    # for now its just taking the SWN positive negative scores
    df = pandas.DataFrame(trainingFrame['SWN_POS'])
    df = df.join(trainingFrame['SWN_NEG'])
    #df = df.join(dataFrame['Created At'])
    #df = df.set_index('Created At')
    date = dataFrame['Created At']
    dateList = []
    for dat in date:
        dateList.append(datetime.strptime(dat,'%a %b %d %H:%M:%S +0000 %Y'))

    df['Time'] = pandas.Series(dateList)

    return df

#Takes input of a data frame with a data index
def plotTimeSeries(frame):
    plt.plot(df['SWN_POS'],df['Time'],'r--',label = "positive")
    plt.plot(df['SWN_NEG'],df['Time'],'b--',label = "negative")
    plt.xlabel("Time")
    plt.ylabel("Score")
    plt.title("Sentiment")
    plt.legend()
    plt.show()


df = pandas.DataFrame(train['SWN_POS'])
df = df.join(train['SWN_NEG'])
df = df.join(data['Created At'])

dateList = []
for dat in date:
    dateList.append(datetime.strptime(dat,'%a %b %d %H:%M:%S +0000 %Y'))

df['Time'] = pandas.Series(dateList)

