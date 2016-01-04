from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

class processing:

    def getCountVector(self,frame):
        vectorizer = CountVectorizer(min_df=1)
        documentmatrix = vectorizer.fit_transform(frame['Tweet'])
        return documentmatrix

    def getTFIDFVector(self,frame):
        vectorizer = TfidfVectorizer(min_df=1)
        documentmatrix = vectorizer.fit_transform(frame['Tweet'])
        return documentmatrix

    def getBigramCountVector(self,frame):
        bigram_vectorizer = CountVectorizer(ngram_range=(1, 2),token_pattern=r'\b\w+\b', min_df=1)
        documentmatrix = bigram_vectorizer.fit_transform(frame['Tweet'])
        return documentmatrix