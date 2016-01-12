
import processing

reload(processing)
p = processing.processing()
dm = p.getCountVector(frame)
print()


##Correlation:     frame.corr('pearson')['Sentiment_SVM']
