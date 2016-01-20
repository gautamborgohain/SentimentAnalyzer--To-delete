
import processing
import pre_processing

reload(processing)
p = processing.processing()
dm = p.getCountVector(frame)
print()

reload(pre_processing)
pp = pre_processing.process_tweets()
df = pp.removeBadTweets(frame)
df.to_csv('/Users/gautamborgohain/Desktop/data_temp.csv')



##Correlation:     frame.corr('pearson')['Sentiment_SVM']


sys.path.extend(['/Users/gautamborgohain/PycharmProjects/SentimentAnalyzer/src'])
import pandas

data = pandas.read_excel('/Users/gautamborgohain/Desktop/SA Files/data_labelled_2.xlsx')
train = pandas.read_csv('/Users/gautamborgohain/Desktop/SA Files/data_temp2.csv')

reload(ML_Classifiers)
ml = ML_Classifiers.ML_classifiers()
