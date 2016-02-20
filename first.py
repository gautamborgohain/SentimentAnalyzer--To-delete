#this project is about taking in sentences or bodies of text, parsing them. creating certain visualizations and then classify the sentence as different emotions or positive negative

filepath = '/Users/gautamborgohain/Desktop/CI/data.csv'



In[3]: import nltk

In[4]: def ie_preprocess(document):
        sentences = nltk.sent_tokenize(docuument)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]
        sentences = [nltk.pos_tag(sent) for sent in sentences]
In[5]: from nltk.corpus import brown
In[6]: help(brown)In[10]: sentence = [("the", "DT"), ("little", "JJ"), ("yellow", "JJ"),("dog","NN"),("barked","VBD"),("at","IN"), ("the","DT"),("cat","NN")]
In[11]: grammer = "NP: {<DT><JJ>*<NN>}"
In[12]: cp = nltk.RegexpParser(grammer)
In[13]: result = cp.parse(sentence)
In[14]: result
Out[14]: Tree('S', [Tree('NP', [('the', 'DT'), ('little', 'JJ'), ('yellow', 'JJ'), ('dog', 'NN')]), ('barked', 'VBD'), ('at', 'IN'), Tree('NP', [('the', 'DT'), ('cat', 'NN')])])
In[15]: result.draw()
In[16]: nltk.app.chunkparser()