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
from nltk import word_tokenize
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tag.stanford import StanfordNERTagger
import sys

class processing:

    config = utilities.getConfigs()
    target = config.get('target')
    tokenizer = Chris_Potts_Tokenizer.Tokenizer()
    # This will be the main processor where the features in the data frame are going to be created.
    def getCountVector(self,frame, getSWM = True, getSubj = True, getPOSTags = True, getTargetFeats = True, getHashTagFeats= True):
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
            tweet = self.cleantweet(tweet) # cleaning
            tweets.append(tweet)

        documentmatrix = vectorizer.fit_transform(tweets).toarray()
        columns = vectorizer.get_feature_names()
        df = pandas.DataFrame(data = documentmatrix, columns= columns)


        if getSWM == True:
            posnegframe = self.getSWN_features(frame)
            df = df.join(posnegframe)

        if getPOSTags == True:
            posframe = self.getPOStagfeatures(frame)
            df = df.join(posframe)

        if getSubj == True:
            subjframe = self.getSubjectvityfeatures(frame)
            df = df.join(subjframe)

        if getTargetFeats == True:
            targetframe = self.target_features(frame)
            df = df.join(targetframe)

        if getHashTagFeats == True:
            hashFrame = self.get_hashTagSentiments(frame)
            df = df.join(hashFrame)

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
        # need to clean the tweets i think - remove the has tags and the atuse signs
        for tweet in frame['Tweet']:
            score = classifier.classify_document(tweet, tagged=False, L=lexicon, a=True, v=True, n=False, r=False, negation=False, verbose=False)
            scores.append(score)
            print("Scoreing using SWN3...", count)
            count += 1
        print('Completed scoring SWN3')
        posnegframe = pandas.DataFrame(scores,columns = ['SWN_POS','SWN_NEG'])
        posnegframe['SWN_Score'] = posnegframe['SWN_POS']/posnegframe['SWN_NEG']
        return posnegframe

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
        tweet_tags = []
        count_tweet = 1
        for tweet in frame['Tweet']:
            tweet = self.cleantweet(tweet)
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

                        if postag in ['NN','NNP','NNS','NNPS']: # make the POS tags to the format used by the MPQA lexicon
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


    def english_postagger(self,tweet):
        english_tagger = StanfordPOSTagger('models/english-bidirectional-distsim.tagger')
        tweet = re.sub('#','at ', tweet)  #removing the hash tags  and replacing with 'at ' its to make sure #smrt is 'at smrt'
        print('POS Tagging')
        tokens = word_tokenize(tweet)
        result = english_tagger.tag(tokens)
        return result

    def english_nertagger(self,tweet):
        english_ner = StanfordNERTagger('classifiers/english.all.3class.distsim.crf.ser.gz')
        #tokens = word_tokenize(sentences)
        #result = english_ner.tag_sents(sentences)
        result = english_ner.tag(tweet.split())
        return result

    def cleantweet(self,tweet):
        tweet = re.sub('url|at_user|rt|\.','',tweet) ## removing these from the tweets
        return tweet

    def target_features(self,frame):
        tweet_target_features = []
        for tweet in frame['Tweet']:
            tags = self.get_hastags(tweet)
            keywords = ['SMRT','mrt','MRT','smrt','Singapore_MRT']
            tokens = word_tokenize(tweet)
            targets_feature = []
            for keyword in keywords:
                if keyword in tags:  ## If i replace elif it if - Thing to note here is that the words which are hash tags will be counted twice here one from tokens and one from hashtags
                    ind = tags.index(keyword)
                    tag = tags[ind]
                    feature = tag+'_hash'
                    targets_feature.append(feature)
                elif keyword in tokens:
                    ind = tokens.index(keyword)
                    tag = tokens[ind] # this is the target
                    adjectives = self.getAdjectves(tweet)#This will get all the adjectives, not just one
                    features = []
                    for adjective in adjectives:
                        adjective = re.sub('-','_',adjective)# this to take care of probelesm for - like east-west/ north-south.. now east_west
                        features.append(tag+'_'+adjective)
                    feature = ' '.join(features)
                    targets_feature.append(feature)

            tweet_target_features.append(' '.join(targets_feature))
        print(tweet_target_features)
        vectorizer = CountVectorizer(min_df=1)
        tweetmatrix = vectorizer.fit_transform(tweet_target_features).toarray()
        columns = vectorizer.get_feature_names()
        print(columns)
        columns = [word.upper() for word in columns]  # uppercasing to avoid conflict of positive negative
        df = pandas.DataFrame(data = tweetmatrix, columns= columns)
        return df

    def get_hastags(self,tweet):
        tweet = tweet.split('#')
        hash_tag = []
        for cen in tweet:
            cen_new = cen.split(' ')
            hash_tag.insert(0,cen_new[0])
            for k in hash_tag:
                if k == '':
                    hash_tag.remove(k)

        return hash_tag

    def getAdjectves(self,tweet):
        postags = ['JJ','JJR','JJS']
        tokens = []
        pos_tags = self.english_postagger(tweet)
        pos_tags_1 = []
        words_1 = []
        for pos in pos_tags:
            pos_tags_1.append(pos[1])

        for pos in pos_tags:
            words_1.append(pos[0])

        for postag in postags:
            if postag in pos_tags_1:
                inds = self.all_indices(postag,pos_tags_1)
                for ind in inds:
                    tokens.append(words_1[ind])

        return tokens

    def all_indices(self,value, qlist):
        indices = []
        idx = -1
        while True:
            try:
                idx = qlist.index(value, idx+1)
                indices.append(idx)
            except ValueError:
                break
        return indices

    def get_hashTagSentiments(self,frame):

        tweets = []
        for tweet in frame['Tweet']:
            tweet = self.cleantweet(tweet)
            tags = self.get_hastags(tweet)
            tweets.append(" ".join(tags))

        frame['Tweet'] = tweets
        df = self.getSubjectvityfeatures(frame)
        columns = df.columns
        new_columns = []
        for column in columns:
            new_columns.append('TAG_'+column)
        df.columns = new_columns
        return df
