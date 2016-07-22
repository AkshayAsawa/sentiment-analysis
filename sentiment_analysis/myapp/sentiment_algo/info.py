from __future__ import division
from math import log, exp
from operator import mul
from collections import Counter
import os
import pickle, re
from math import e
from django.contrib.staticfiles.templatetags.staticfiles import static
class MyDict(dict):
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return 0

pos = MyDict()
neg = MyDict()
features = set()
totals = [0, 0]
delchars = ''.join(c for c in map(chr, range(128)) if not c.isalnum())
static_path = 'C:\Users\Akshay.Asawa\Desktop\hackathon\ce2016-bits-please\sentiment_analysis\myapp\sentiment_algo\\'
# CDATA_FILE = "countdata.pickle"
FDATA_FILE = "reduceddata.pickle"


def percentage_confidence(conf):
	return 100.0 * e ** conf / (1 + e**conf)


def negate_sequence(text):
    """
    Detects negations and transforms negated words into "not_" form.
    """
    negation = False
    delims = "/#@?.,!:;"
    result = []
    if type(text) is not unicode:
        text = str(text)
    words = text.split()
    prev = None
    pprev = None
    for word in words:
        # stripped = word.strip(delchars)
        stripped = word.strip(delims).lower()
        negated = "not_" + stripped if negation else stripped
        result.append(negated)
        if prev:
            bigram = prev + " " + negated
            result.append(bigram)
            if pprev:
                trigram = pprev + " " + bigram
                result.append(trigram)
            pprev = prev
        prev = negated

        if any(neg in word for neg in ["not", "n't", "no"]):
            negation = not negation

        if any(c in word for c in delims):
            negation = False

    return result

def classify2(text):



    """
    For classification from pretrained data
    """
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0): return True, 0
    # Probability that word occurs in pos documents
    pos_prob = sum(log((pos[word] + 1) / (2 * totals[0])) for word in words)
    neg_prob = sum(log((neg[word] + 1) / (2 * totals[1])) for word in words)
    return (pos_prob > neg_prob, abs(pos_prob - neg_prob))


def main_classify(text_list):
    return_list = []
    for text in text_list:
        flag, confidence = classify2(text)
        if confidence > 0.5:
            sentiment = "4" if flag else "0"
        else:
            sentiment = "2"

        conf = "%.4f" % percentage_confidence(confidence)
        return_list.append({'text': text, 'score':int(sentiment), 'confidence':conf})
    return return_list



def classify_demo(text):
    words = set(word for word in negate_sequence(text) if word in pos or word in neg)
    if (len(words) == 0):
        print "No features to compare on"
        return True

    pprob, nprob = 0, 0
    for word in words:
        pp = log((pos[word] + 1) / (2 * totals[0]))
        np = log((neg[word] + 1) / (2 * totals[1]))
        print "%15s %.9f %.9f" % (word, exp(pp), exp(np))
        pprob += pp
        nprob += np

    print ("Positive" if pprob > nprob else "Negative"), "log-diff = %.9f" % abs(pprob - nprob)

def feature_selection_trials():
    """
    Select top k features. Vary k and plot data
    """
    posi = 0
    negi = 0
    totalsi = 0
    retrain = False
    static_path = 'C:\Users\Akshay.Asawa\Desktop\hackathon\ce2016-bits-please\sentiment_analysis\myapp\sentiment_algo\\'

    if not retrain and os.path.isfile(static_path + FDATA_FILE):
        posi, negi, totalsi = pickle.load(open(static_path + FDATA_FILE))
        return

def setup():

    global pos, neg, totals, features
    t_pos = open(static_path + "positives").readlines()
    t_neg = open(static_path + "negatives").readlines()
    totals = [3321176, 3320100]

    for i in t_pos:
        if not i == '':
            i.strip('\n')
            i = i[::-1]
            score = ""
            sentence = ""
            found = 0
            for x in range(len(i)):
                if i[x] == ' ' and found == 0:
                    found = 1
                    continue
                if found == 0:
                    score += i[x]
                else:
                    sentence += i[x]
            # print sentence[::-1],score[::-1]
            pos[sentence[::-1]] = int(score[::-1])

    for i in t_neg:
        if not i == '':
            i.strip("\n")
            i = i[::-1]
            score = ""
            sentence = ""
            found = 0
            for x in range(len(i)):
                if i[x] == ' ' and found == 0:
                    found = 1
                elif found == 0:
                    score += i[x]
                elif found == 1:
                    sentence += i[x]
            neg[sentence[::-1]] = int(score[::-1])
        else:
            print "HOLAA"


def main(text_list):
    setup()
    return main_classify(text_list)
