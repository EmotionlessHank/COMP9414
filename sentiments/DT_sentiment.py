import re
import sys
import numpy as np
import pandas as pd
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report

# read file from parameter input
data_set_file_input, test_set_file_input = sys.argv[1], sys.argv[2]

# use pd to read the file into training and test
training = pd.read_csv(data_set_file_input, sep='\t', header=None)
testing = pd.read_csv(test_set_file_input, sep='\t', header=None)

# get sentence and id from training and test
testing_id = np.array(testing[0])
training_sentence, training_y = np.array(training[1]), np.array(training[2])
testing_sentence, testing_y = np.array(testing[1]), np.array(testing[2])


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
        # remove_special_char = re.sub(
        #     u"([^\u0030-\u0039\u0041-\u005a\u0061-\u007a\u005F\u0023-\u0026\u0040])", " ",
        #     remove_url_format)
        # result.append(remove_special_char)
        result.append(remove_url_format)
    return result


valid_train_sentence,valid_test_sentence = data_preprocessing(training_sentence),data_preprocessing(testing_sentence)

# use CountVectorizer() to limit a word have at least 2 chars
# create count vectorizer and fit it with training data

# filter setting, using 'r' to ignore backslash
token = r'[#@_$%\w\d]{2,}'

# store the result into counter, add 'max_feature' to limit the number of feature
# lowercase default is True and convert and words to lowercase,
# if u want to remain the uppercase, set it to lowercase = False
counter = CountVectorizer(token_pattern=token, max_features=1000, lowercase=False)

X_train_bag_of_words = counter.fit_transform(valid_train_sentence)

# transform the test data into bag of words created with fit_transform
X_test_bag_of_words = counter.transform(valid_test_sentence)
# set the min samples leaf as 1% of training sets.
min_value = int(len(training_sentence)//100)
clf = tree.DecisionTreeClassifier(min_samples_leaf=min_value, criterion='entropy', random_state=0)
model = clf.fit(X_train_bag_of_words, training_y)
predict_y = model.predict(X_test_bag_of_words)

# print the valid output
for i in range(len(testing_sentence)):
    print(f'{testing_id[i]} {predict_y[i]} ')

# print out the classification report
# predict_and_test(model, X_test_bag_of_words)
