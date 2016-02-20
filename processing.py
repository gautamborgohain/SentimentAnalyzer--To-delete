from sklearn.feature_extraction.text import CountVectorizer
import pandas
import re
from nltk import pos_tag
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tag.stanford import StanfordNERTagger

target = 'Sentiment_SVM'



def regex_stuff(tweet):
    # Convert to lower case
    tweet = tweet.lower()
    # Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)
    # Convert @username to AT_USER
    tweet = re.sub('@[^\s]+', 'AT_USER', tweet)
    # Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    # Replace #word with word
    # tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    # trim
    tweet = tweet.strip('\'"')

    return tweet

def removeStopWords(tokens):
    stopwordsList = stopwords.words('english')
    stopwordsList.append('AT_USER')
    stopwordsList.append('URL')
    stopwordsList.append('at_user')
    stopwordsList.append('url')
    filtered_tokens = [word for word in tokens if word not in stopwordsList]
    return filtered_tokens


def removeBadTweets(tweetsdf):
    newDF = pandas.DataFrame(columns=tweetsdf.columns)
    baddatacount = 1
    for i in range(1, len(tweetsdf)):
        tweet = tweetsdf.get_value(i, 'Tweet')
        tweet = regex_stuff(tweet)  # remove using the regex function
        tweet = tweet.encode('ascii', 'ignore').decode('ascii')  # remove the weird characters
        if tweet.startswith('I\'m at ') or tweet.startswith('i\'m at '):
            baddatacount += 1
        else:
            tweetsdf = tweetsdf.set_value(i, 'Tweet', tweet)
            newDF = newDF.append(tweetsdf[i:i + 1])
            # print(tweetsdf.ix[i])

    print("Completed, Bad count = ", baddatacount)
    print(newDF.head())

    return newDF



# wont be needing this function
def initialFeatureVector(frame):
    features = []
    labels = []
    for row in range(0, len(frame) - 1):
        feature_vector = []
        tweet = frame.iloc[row, 1]  # tweet column
        sentiment = frame.iloc[row, 8]  # 8= Sentiment_SVM, 9 = Sentiment_Vb  10 = Sentiment_Subj
        tokens = word_tokenize.tokenize(tweet)
        # tokens = word_tokenize(tweet)
        # tokens = tweet.split()
        tokens = removeStopWords(tokens)
        feature_vector.append(tokens)
        features.append(feature_vector)
        labels.append(sentiment)
    return {'feature_vector': features, 'labels': labels}

#
# def getSWN_features(frame):
#     """
#
#     :rtype: pandas dataframe
#     """
#     lexicon = sentlex.SWN3Lexicon()
#     classifier = sentlex.sentanalysis.BasicDocSentiScore()
#     scores = []
#     count = 1
#     # need to clean the tweets i think - remove the has tags and the atuse signs
#     for tweet in frame['Tweet']:
#         score = classifier.classify_document(tweet, tagged=False, L=lexicon, a=True, v=True, n=False, r=False,
#                                              negation=False, verbose=False)
#         scores.append(score)
#         print("Scoreing using SWN3...", count)
#         count += 1
#     print('Completed scoring SWN3')
#     posnegframe = pandas.DataFrame(scores, columns=['SWN_POS', 'SWN_NEG'])
#     posnegframe['SWN_Score'] = posnegframe['SWN_POS'] / posnegframe['SWN_NEG']
#     return posnegframe


def getPOStagfeatures(frame):
    """

    :rtype: pandas dataframe
    """
    tagsoftweet = []
    reg = re.compile(r'at_user|rt|,')
    count = 1
    for tweet in frame['Tweet']:
        tweet = re.sub(reg, '', tweet)  # stripping it off stuff
        print('Tagging tweet', count)
        postaggedtweet = pos_tag(word_tokenize(tweet))  # this one is pos atgged..list inside list : token[1] for tag
        tags = []
        for token in postaggedtweet:
            tags.append(token[1])
        tagsoftweet.append(' '.join(tags))
        count += 1

    vectorizer = CountVectorizer(min_df=1)
    tweetmatrix = vectorizer.fit_transform(tagsoftweet).toarray()
    columns = vectorizer.get_feature_names()
    columns = [word.upper() for word in columns]  # uppercasing to avoid conflict of in and other words
    df = pandas.DataFrame(data=tweetmatrix, columns=columns)
    print('Completed POS tagging')
    return df


def getSubjectvityfeatures(frame):
    """

    :rtype: pandas dataframe
    """
    lexicon = pandas.read_csv('/Users/gautamborgohain/PycharmProjects/SentimentAnalyzer/subjectivity.csv')
    tweet_tags = []
    count_tweet = 1
    for tweet in frame['Tweet']:
        tweet = cleantweet(tweet)
        typeList = []
        priorpolarityList = []
        count_word = 0  # this counter is for the pos tagging. traces the words in the tweet so that the idrect index of the tag can be accesses
        print('Performing subjectivity analysis of Tweet ', count_tweet)
        count_tweet += 1
        for word in word_tokenize(tweet):
            result = lexicon[lexicon.word1 == word]
            if len(result) != 0:  # word is there in the lexicon
                if len(result) == 1:  # this case is handling the ones where the there is only one record of the word
                    typeList.append(result.iloc[0][0])
                    priorpolarityList.append(result.iloc[0][5])
                if len(
                        result) > 1:  # this is if there are more than one instances of the owrd in the lexicon then the pos tag is checked
                    print('Have to tag POS, Hold On!')
                    poslist = pos_tag(word_tokenize(tweet))
                    postag = poslist[count_word][1]

                    if postag in ['NN', 'NNP', 'NNS',
                                  'NNPS']:  # make the POS tags to the format used by the MPQA lexicon
                        postag = 'noun'
                    elif postag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']:
                        postag = 'verb'
                    elif postag in ['RB', 'RBR', 'RBS']:
                        postag = 'adverb'
                    elif postag in ['JJ', 'JJR', 'JJS']:
                        postag = 'adj'

                    second_result = result[result.pos1 == postag]
                    if len(
                            second_result) != 0:  # this is to check if the pos tag that the word was tagged is there in the lexicon for that word
                        typeList.append(second_result.iloc[0][0])
                        priorpolarityList.append(second_result.iloc[0][5])

            count_word += 1

        tweet_tags.append(' '.join(typeList) + ' ' + ' '.join(priorpolarityList))

    vectorizer = CountVectorizer(min_df=1)
    tweetmatrix = vectorizer.fit_transform(tweet_tags).toarray()
    columns = vectorizer.get_feature_names()
    columns = [word.upper() for word in columns]  # uppercasing to avoid conflict of positive negative
    df = pandas.DataFrame(data=tweetmatrix, columns=columns)
    print('Completed Subjective Analysis')
    return df


def english_postagger(tweet):
    english_tagger = StanfordPOSTagger('models/english-bidirectional-distsim.tagger')
    tweet = re.sub('#', 'at ',
                   tweet)  # removing the hash tags  and replacing with 'at ' its to make sure #smrt is 'at smrt'
    print('POS Tagging')
    tokens = word_tokenize(tweet)
    result = english_tagger.tag(tokens)
    return result


def english_nertagger(tweet):
    english_ner = StanfordNERTagger('classifiers/english.all.3class.distsim.crf.ser.gz')
    # tokens = word_tokenize(sentences)
    # result = english_ner.tag_sents(sentences)
    result = english_ner.tag(tweet.split())
    return result


def cleantweet(tweet):
    tweet = re.sub('url|at_user|rt|\.', '', tweet)  ## removing these from the tweets
    return tweet


def target_features(frame):
    tweet_target_features = []
    for tweet in frame['Tweet']:
        tags = get_hastags(tweet)
        keywords = ['SMRT', 'mrt', 'MRT', 'smrt', 'Singapore_MRT']
        tokens = word_tokenize(tweet)
        targets_feature = []
        for keyword in keywords:
            if keyword in tags:  ## If i replace elif it if - Thing to note here is that the words which are hash tags will be counted twice here one from tokens and one from hashtags
                ind = tags.index(keyword)
                tag = tags[ind]
                feature = tag + '_hash'
                targets_feature.append(feature)
            elif keyword in tokens:
                ind = tokens.index(keyword)
                tag = tokens[ind]  # this is the target
                adjectives = getAdjectves(tweet)  # This will get all the adjectives, not just one
                features = []
                for adjective in adjectives:
                    adjective = re.sub('-', '_',
                                       adjective)  # this to take care of probelesm for - like east-west/ north-south.. now east_west
                    features.append(tag + '_' + adjective)
                feature = ' '.join(features)
                targets_feature.append(feature)

        tweet_target_features.append(' '.join(targets_feature))
    print(tweet_target_features)
    vectorizer = CountVectorizer(min_df=1)
    tweetmatrix = vectorizer.fit_transform(tweet_target_features).toarray()
    columns = vectorizer.get_feature_names()
    print(columns)
    columns = [word.upper() for word in columns]  # uppercasing to avoid conflict of positive negative
    df = pandas.DataFrame(data=tweetmatrix, columns=columns)
    return df


def get_hastags(tweet):
    tweet = tweet.split('#')
    hash_tag = []
    for cen in tweet:
        cen_new = cen.split(' ')
        hash_tag.insert(0, cen_new[0])
        for k in hash_tag:
            if k == '':
                hash_tag.remove(k)

    return hash_tag


def getAdjectves(tweet):
    postags = ['JJ', 'JJR', 'JJS']
    tokens = []
    pos_tags = pos_tag(tweet)
    pos_tags_1 = []
    words_1 = []
    for pos in pos_tags:
        pos_tags_1.append(pos[1])

    for pos in pos_tags:
        words_1.append(pos[0])

    for postag in postags:
        if postag in pos_tags_1:
            inds = all_indices(postag, pos_tags_1)
            for ind in inds:
                tokens.append(words_1[ind])

    return tokens


def all_indices(value, qlist):
    indices = []
    idx = -1
    while True:
        try:
            idx = qlist.index(value, idx + 1)
            indices.append(idx)
        except ValueError:
            break
    return indices


def get_hashTagSentiments(frame):
    tweets = []
    for tweet in frame['Tweet']:
        tweet = cleantweet(tweet)
        tags = get_hastags(tweet)
        tweets.append(" ".join(tags))

    frame['Tweet'] = tweets
    df = getSubjectvityfeatures(frame)
    columns = df.columns
    new_columns = []
    for column in columns:
        new_columns.append('TAG_' + column)
    df.columns = new_columns
    return df


# This will be the main processor where the features in the data frame are going to be created.
def getCountVector(frame, getSWM=True, getSubj=True, getPOSTags=True, getTargetFeats=True, getHashTagFeats=True):
    vectorizer = CountVectorizer(min_df=1)
    tweets = []

    # this part is just to get rid of the emoticons and stuff making it impossible to write to csv
    try:
        # UCS-4
        highpoints = re.compile(u'[U00010000-U0010ffff]')
    except re.error:
        # UCS-2
        highpoints = re.compile(u'[uD800-uDBFF][uDC00-uDFFF]')
    for tweet in frame['Tweet']:
        tweet = highpoints.sub('', tweet)
        tweet = tweet.encode('ascii', 'ignore').decode('ascii')
        tweet = cleantweet(tweet)  # cleaning
        tweets.append(tweet)

    documentmatrix = vectorizer.fit_transform(tweets).toarray()
    columns = vectorizer.get_feature_names()
    df = pandas.DataFrame(data=documentmatrix, columns=columns)



    # Negations

    # Emoticon

    # Punctuation

    # Elongated words

    # URL ??


    df = df.join(frame[target])
    return df


# if getSWM == True:
    #     posnegframe = getSWN_features(frame)
    #     df = df.join(posnegframe)
    #
    # if getPOSTags == True:
    #     posframe = getPOStagfeatures(frame)
    #     df = df.join(posframe)
    #
    # if getSubj == True:
    #     subjframe = getSubjectvityfeatures(frame)
    #     df = df.join(subjframe)
    #
    # if getTargetFeats == True:
    #     targetframe = target_features(frame)
    #     df = df.join(targetframe)
    #
    # if getHashTagFeats == True:
    #     hashFrame = get_hashTagSentiments(frame)
    #     df = df.join(hashFrame)