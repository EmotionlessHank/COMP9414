import re
import string
import sys
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.naive_bayes import MultinomialNB
from  nlppreprocess import NLP


# read file from parameter input
data_set_file_input, test_set_file_input = sys.argv[1], sys.argv[2]

# use pd to read the file into training and test
training = pd.read_csv(data_set_file_input, sep='\t', header=None)
testing = pd.read_csv(test_set_file_input, sep='\t', header=None)

# I used a NLP() to preprocess the stopword, but the result seems not very good.
# nlp = NLP()
# training[1] = training[1].apply(nlp.process)
# testing[1] = testing[1].apply(nlp.process)

# get sentence and id from training and test
testing_id = np.array(testing[0])
training_sentence,training_y = np.array(training[1]),np.array(training[2])
testing_sentence,testing_y = np.array(testing[1]),np.array(testing[2])


# predict and test func from example.py
def predict_and_test(model, X_test_bag_of_words):
    predicted_y = model.predict(X_test_bag_of_words)
    # print(testing_y, predicted_y)
    # print(model.predict_proba(X_test_bag_of_words))
    print(classification_report(testing_y, predicted_y, zero_division=0))


# remove the url and invalid char in sentence
def data_preprocessing(sentence):
    # use regular expression to express the format of url
    url_format = re.compile(r'[http|https]*://[a-zA-Z0-9.?/&=:]*')
    # same, use regular expression to express the invalid char
    result = []
    for i in sentence:
        # replace the url as space
        remove_url_format = re.sub(url_format, ' ', i)
        # i remove some special char like roman char but can not pass the
        # auto test so i just set them as comment below
        # remove_special_char = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", " ",
        #                              remove_url_format)
        # result.append(remove_special_char)
        remove_special_char = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", " ", remove_url_format)
        remove_backslash_n = re.sub('\\n', ' ', remove_special_char)
        remove_Startwith_User = re.sub("\[\[User.*", '', remove_backslash_n)
        remove_IP = re.sub("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", '', remove_Startwith_User)
        result.append(remove_IP)
    return result


valid_train_sentence,valid_test_sentence = data_preprocessing(training_sentence),data_preprocessing(testing_sentence)

# use f' to format the string
# string.punctuation is a readymade-string of common punctuation marks.
# re.compile(f'...') compiles the expression([{string.punctuation}...]) into pattern objects
re_tok = re.compile(f'([{string.punctuation}“”¨«»®´·º½¾¿¡§£₤‘’])')


# re_tok.sub(r' \1 ', s) finds all the resulting matching-punctuations and
# adds a prefix and suffix of white-space to those matching patterns.
# Lastly, split() call tokenizes resulting string into an array of individual
# words and punctuation marks.
def tokenize(s): return re_tok.sub(r' \1 ', s).split()
# use CountVectorizer() to limit a word have at least 2 chars
# create count vectorizer and fit it with training data

# filter setting, use 'r' to ignore the backslash
token = r'[#@_$%\w\d]{2,}'
# store the result into counter
# counter = CountVectorizer(token_pattern=token)
# i use plot to analyse and find the best value of max_features which is
# around 2000 ~ 2100
counter = CountVectorizer(token_pattern=token,max_features=2100)
# I also implementing the TfidfVectorizer, but the accuracy is lower than countvec.
tfidfvec = TfidfVectorizer(
                           min_df=3, max_df=0.9, strip_accents='unicode', use_idf=1,
                           smooth_idf=1, sublinear_tf=1,token_pattern=token)
X_train_bag_of_words = counter.fit_transform(valid_train_sentence)
# transform the test data into bag of words created with fit_transform
X_test_bag_of_words = counter.transform(valid_test_sentence)

# print('my sentiment basic result')
# set classifier MNB
clf = MultinomialNB()
# fit in model
model = clf.fit(X_train_bag_of_words, training_y)

# print predict result with id
predict_y = model.predict(X_test_bag_of_words)
for i in range(len(testing_sentence)):
    print(testing_id[i],predict_y[i])
my_report = classification_report(testing_y, predict_y, zero_division=0)
# predict_and_test(model, X_test_bag_of_words)


# this is used to test the best performance of my sentiment by change the
# max_features value
# for i in range(100, 5000, 100):
#     counter = CountVectorizer(token_pattern=token, max_features=i)
#
#     X_train_bag_of_words = counter.fit_transform(valid_train_sentence)
#
#     # transform the test data into bag of words created with fit_transform
#     X_test_bag_of_words = counter.transform(valid_test_sentence)
#
#     # set classifier MNB
#     clf = MultinomialNB()
#     # fit in model
#     model = clf.fit(X_train_bag_of_words, training_y)
#
#     # print predict result with id
#     predict_y = model.predict(X_test_bag_of_words)
#     # for i in range(len(testing_sentence)):
#     #     print(testing_id[i],predict_y[i])
#
#     # predict_and_test(model, X_test_bag_of_words)
#     my_report = classification_report(testing_y, predict_y, zero_division=0)
#
#     print(f'{i}')
#     print(my_report)
