from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pre_processing
import Chris_Potts_Tokenizer
import pandas
import re
import sentlex
from nltk import pos_tag
from nltk import word_tokenize
import utilities

class processing:

    config = utilities.getConfigs()
    target = config.get['target']
    tokenizer = Chris_Potts_Tokenizer.Tokenizer()
    # This will be the main processor where the features in the data frame are going to be created.
    def getCountVector(self,frame, getSWM = True, getSubj = True, getPOSTags = True):
        vectorizer = CountVectorizer(min_df=1)
        tweets = []

        #this part is just to get rid of the emoticons and stuff making it impossible to write to csv
        try:
        # UCS-4
            highpoints = re.compile(u'[U00010000-U0010ffff]')
        except re.error:
         # UCS-2
             highpoints = re.compile(u'[uD800-uDBFF][uDC00-uDFFF]')
        for tweet in frame['Tweet']:
            tweet = highpoints.sub('',tweet)
            tweet = tweet.encode('ascii', 'ignore').decode('ascii')
            tweets.append(tweet)

        documentmatrix = vectorizer.fit_transform(tweets).toarray()
        columns = vectorizer.get_feature_names()
        df = pandas.DataFrame(data = documentmatrix, columns= columns)

        if getSWM == True:
            scores = self.getSWN_features(frame)
            posnegframe = pandas.DataFrame(scores,columns = ['SWN_POS','SWN_NEG'])
            df = df.join(posnegframe)

        if getPOSTags == True:
            posframe = self.getPOStagfeatures(frame)
            df = df.join(posframe)

        if getSubj == True:
            subjframe = self.getSubjectvityfeatures(frame)
            df = df.join(subjframe)

        df = df.join(frame[self.config.get('target')])
        return df

    def getTFIDFVector(self,frame):
        vectorizer = TfidfVectorizer(min_df=1)
        documentmatrix = vectorizer.fit_transform(frame['Tweet'])
        return documentmatrix

    def getBigramCountVector(self,frame):
        bigram_vectorizer = CountVectorizer(ngram_range=(1, 2),token_pattern=r'\b\w+\b', min_df=1)
        documentmatrix = bigram_vectorizer.fit_transform(frame['Tweet'])
        return documentmatrix

    # wont be needing this function
    def initialFeatureVector(self,frame):
        features = []
        labels = []

        tokenizer = Chris_Potts_Tokenizer.Tokenizer()
        pp = pre_processing.process_tweets()
        for row in range(0,len(frame)-1):
            feature_vector = []
            tweet = frame.iloc[row,1]# tweet column
            sentiment = frame.iloc[row,8]# 8= Sentiment_SVM, 9 = Sentiment_Vb  10 = Sentiment_Subj
            tokens = tokenizer.tokenize(tweet)
            #tokens = word_tokenize(tweet)
            #tokens = tweet.split()
            tokens = pp.removeStopWords(tokens)
            feature_vector.append(tokens)
            features.append(feature_vector)
            labels.append(sentiment)
        return {'feature_vector' : features, 'labels': labels}

    def getSWN_features(self,frame):
        """

        :rtype: pandas dataframe
        """
        lexicon = sentlex.SWN3Lexicon()
        classifier = sentlex.sentanalysis.BasicDocSentiScore()
        scores = []
        count = 1
        for tweet in frame['Tweet']:
            score = classifier.classify_document(tweet, tagged=False, L=lexicon, a=True, v=True, n=False, r=False, negation=False, verbose=False)
            scores.append(score)
            print("Scoreing using SWN3...", count)
            count += 1
        print('Completed scoring SWN3')
        return scores

    def getPOStagfeatures(self,frame):
        """

        :rtype: pandas dataframe
        """
        tagsoftweet = []
        reg = re.compile(r'at_user|rt|,')
        count = 1
        for tweet in frame['Tweet']:
            tweet = re.sub(reg,'',tweet) #stripping it off stuff
            print('Tagging tweet',count)
            postaggedtweet = pos_tag(word_tokenize(tweet)) # this one is pos atgged..list inside list : token[1] for tag
            tags = []
            for token in postaggedtweet:
                tags.append(token[1])
            tagsoftweet.append(' '.join(tags))
            count +=1

        vectorizer = CountVectorizer(min_df=1)
        tweetmatrix = vectorizer.fit_transform(tagsoftweet).toarray()
        columns = vectorizer.get_feature_names()
        columns = [word.upper() for word in columns]  # uppercasing to avoid conflict of in and other words
        df = pandas.DataFrame(data = tweetmatrix, columns= columns)
        print('Completed POS tagging')
        return df

    def getSubjectvityfeatures(self,frame):
        """

        :rtype: pandas dataframe
        """
        lexicon  = pandas.read_csv(self.config.get('SubjLexiconPath'))
        reg = re.compile(r'at_user|rt|,|#')
        tweet_tags = []
        count_tweet = 1
        for tweet in frame['Tweet']:
            tweet = re.sub(reg,'',tweet) #stripping it off stuff
            typeList = []
            priorpolarityList = []
            count_word = 0 # this counter is for the pos tagging. traces the words in the tweet so that the idrect index of the tag can be accesses
            print('Performing subjectivity analysis of Tweet ', count_tweet)
            count_tweet+=1
            for word in word_tokenize(tweet):
                result = lexicon[lexicon.word1 == word]
                if len(result) != 0: # word is there in the lexicon
                    if len(result) == 1:  # this case is handling the ones where the there is only one record of the word
                        typeList.append(result.iloc[0][0])
                        priorpolarityList.append(result.iloc[0][5])
                    if len(result) > 1:  # this is if there are more than one instances of the owrd in the lexicon then the pos tag is checked
                        print('Have to tag POS, Hold On!')
                        poslist = pos_tag(word_tokenize(tweet))
                        postag = poslist[count_word][1]

                        if postag in ['NN','NNP','NNS','NNPS']:
                            postag = 'noun'
                        elif postag in ['VB','VBD','VBG','VBN','VBP','VBZ']:
                            postag = 'verb'
                        elif postag in ['RB','RBR','RBS']:
                            postag = 'adverb'
                        elif postag in ['JJ','JJR','JJS']:
                            postag  = 'adj'

                        second_result = result[result.pos1 == postag]
                        if len(second_result) != 0: # this is to check if the pos tag that the word was tagged is there in the lexicon for that word
                            typeList.append(second_result.iloc[0][0])
                            priorpolarityList.append(second_result.iloc[0][5])

                count_word+=1

            tweet_tags.append(' '.join(typeList)+' '+ ' '.join(priorpolarityList))

        vectorizer = CountVectorizer(min_df=1)
        tweetmatrix = vectorizer.fit_transform(tweet_tags).toarray()
        columns = vectorizer.get_feature_names()
        columns = [word.upper() for word in columns]  # uppercasing to avoid conflict of positive negative
        df = pandas.DataFrame(data = tweetmatrix, columns= columns)
        print('Completed Subjective Analysis')
        return df

