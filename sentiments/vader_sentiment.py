import sys
import pandas as pd
import numpy as np
import re

from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report


# read file from parameter input
data_set_file_input = sys.argv[1]
test_set_file_input = sys.argv[2]

# use pd to read the file into training and test
training = pd.read_csv(data_set_file_input, sep='\t', header=None)
testing = pd.read_csv(test_set_file_input, sep='\t', header=None)

# get sentence and id from training and test
testing_id = np.array(testing[0])
training_sentence = np.array(training[1])
training_y = np.array(training[2])
testing_sentence = np.array(testing[1])
testing_y = np.array(testing[2])


# predict and test func from example.py
def predict_and_test(model, X_test_bag_of_words):
    predicted_y = model.predict(X_test_bag_of_words)
    print(testing_y, predicted_y)
    print(model.predict_proba(X_test_bag_of_words))
    print(classification_report(testing_y, predicted_y, zero_division=0))


# remove the url and invalid char in sentence
def data_preprocessing(sentence):
    # use regular expression to express the format of url
    url_format = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=:]*')
    # same, use regular expression to express the invalid char
    invalid_char = r'[^#@_$%\s\w\d]'
    result = []
    for i in sentence:
        # replace the url as space
        remove_url_format = re.sub(url_format, ' ', i)
        # remove the invalid chars
        # remove_invalid_char = re.sub(invalid_char, '', remove_url_format)
        remove_special_char = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\u005F\u0023-\u0026\u0040])", " ",
                                     remove_url_format)
        result.append(remove_special_char)
        # result.append(remove_url_format)
    return result


# print(data_preprocessing(training_sentence))

valid_train_sentence = data_preprocessing(training_sentence)
valid_test_sentence = data_preprocessing(testing_sentence)

# analyse with VADER
Vader_positive = 0
Vader_negative = 0
Vader_neutral = 0
predict_result = []
analyser = SentimentIntensityAnalyzer()
for text in testing_sentence:
    score = analyser.polarity_scores(text)
    if score['compound'] >= 0.05:
        Vader_positive +=1
        predict_result.append('positive')
        # print(text+": "+"VADER positive")
    elif score['compound'] <= -0.05:
        Vader_negative +=1
        predict_result.append('negative')
        # print(text+": "+"VADER negative")
    else:
        Vader_neutral +=1
        predict_result.append('neutral')
        # print(text+": "+"VADER neutral")

print(classification_report(testing_y,predict_result))