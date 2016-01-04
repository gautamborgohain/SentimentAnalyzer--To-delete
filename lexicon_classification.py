import nltk
import sentlex
from sentlex import sentanalysis
from openpyxl import load_workbook
from nltk.corpus import stopwords

filepath = '/Users/gautamborgohain/Desktop/Parsed-anime-Comments.Rdata.xlsx'
sheetname = 'Parsed-anime-Comments.Rdata'
text_col_no = 9
output_start_col_no = 11

sample_text='''we had a great time at the tirreno hotel, very friendly and helpful, nothing was ever too much trouble.
the rooms were in excellent condition, very clean and comfortable.'''


#returns tupple of positive and negative scores
def posnegscore(text):
    lexicon = sentlex.SWN3Lexicon()
    classifier = sentlex.sentanalysis.BasicDocSentiScore()
    result = classifier.classify_document(text, tagged=False, L=lexicon, a=True, v=True, n=False, r=False, negation=False, verbose=False)
    return result

def neutrality_check(positive,negative):
    if (positive>negative and (positive - negative) > 0.2):
        text = "Mostly positive"
    elif(negative>positive and negative-positive>0.2):
        text = "Mostly negative"
    else:
        text = "Maybe Neutral"
    return text

def main():
    wb = load_workbook(filename = filepath)
    sheet = wb[sheetname]
    total_rows = sheet.get_highest_row()
    first_row = 2
    for i in range(first_row,20):
        text = sheet._get_cell(i,text_col_no).value
        score = posnegscore(text)
        positive = score[0]
        negative = score[1]
        comment = neutrality_check(positive,negative)
        sheet._get_cell(i,output_start_col_no).value = positive
        sheet._get_cell(i,output_start_col_no+1).value = negative
        sheet._get_cell(i,output_start_col_no+2).value = comment
        print "Scoring %d" %i
    print "Completed evaluating. Now saving file"
    wb.save(filename=filepath)

main()

'''
tokens = nltk.word_tokenize(text)
filtered_words = [word for word in tokens if word not in stopwords.words('english')]
anger_words = "angry furious rage anger dare stupid idiot absurd"
sum = 1
for word in filtered_words:
    if word in anger_words:
        sum += 1

score = sum/len(filtered_words)
'''