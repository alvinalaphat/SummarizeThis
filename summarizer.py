import flask
from flask import Flask, render_template, request
import heapq
import re
import gunicorn
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('summarizer.html')

@app.route('/', methods=['POST'])
def summarize():

    #preprocessing
    words = re.sub(r'\[[0-9]*\]', ' ', request.form['words'])
    words = re.sub(r'\s+', ' ', words)
    formatted_words = re.sub('[^a-zA-Z]', ' ', words)
    formatted_words = re.sub(r'\s+', ' ', formatted_words)

    def intersection(lst1, lst2): 
        return list(set(lst1) & set(lst2)) 

    transition_words = ['for example', 'for instance', 'additionally', 'moreover', 'however', 'on the other hand']

    word_sents = nltk.sent_tokenize(words)
    word_sents = [sent for sent in word_sents if not any(word in transition_words for word in sent.lower().split())]
    word_sents = [sent for sent in word_sents if '?' not in sent]
    
    sum_sents = int(.25 * len(word_sents))

    word_freq = {}
    for word in nltk.word_tokenize(formatted_words):
        if word not in stopwords.words('english'):
            if word not in word_freq.keys():
                word_freq[word] = 1
            else:
                word_freq[word] += 1
    
    max_freq = max(word_freq.values())
    for word in word_freq.keys():
        word_freq[word] = (word_freq[word]/max_freq)

    sentence_scores = {}
    sentence_map = {}
    sent_number = 0
    for sent in word_sents:
        sentence_map[sent] = sent_number
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_freq.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_freq[word]
                    else:
                        sentence_scores[sent] += word_freq[word]
        sent_number = sent_number + 1
    summary_sentences = heapq.nlargest(sum_sents, sentence_scores, key=sentence_scores.get)
    ordered = sorted(summary_sentences[1:], key=sentence_map.get)

    sum = summary_sentences[0] + ' ' + ' '.join(ordered)

    return render_template('summary.html', summary=sum)

if __name__ == '__main__':
    app.run(debug=True)