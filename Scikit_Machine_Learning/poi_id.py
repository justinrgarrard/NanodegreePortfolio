#!/usr/bin/python

import sys
import pickle
import numpy as np
import pprint
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data, test_classifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

poi_list = [name for name in data_dict.keys() if data_dict[name]['poi']]
print('POI Count: {}\tNon-POI Count: {}'.format(
    len(poi_list), len(data_dict) - len(poi_list)))

# We'll make use of an Adaboost classifier, so overfitting and
# feature overload are less of a concern.
features_list = ['poi', 'bonus', 'total_stock_value',
                 'expenses', 'other', 'deferred_income']
# features_list = ['poi', 'total_messages'] + \
#                 [f for f in data_dict[poi_list[0]].keys() if f != 'email_address'
#                  and f != 'poi']


### Task 2: Remove outliers

print('Cleaning in process...')

# Get rid of the "total" row
del(data_dict['TOTAL'])

# James Bannantine (former CEO and non-POI)
# Has a reported salary of $477
del(data_dict['BANNANTINE JAMES M'])

# Rodney Gray (former CEO and non-POI)
# Has a reported salary of $6,615
del(data_dict['GRAY RODNEY'])

# Robert Belfer (former Director and non-POI)
# Has a negative total stock value (probable data entry error)
del(data_dict['BELFER ROBERT'])

# Sanjay Bhatnagar (non-POI)
# Has a positive restricted_stock_deferred (probable data entry error)
del(data_dict['BHATNAGAR SANJAY'])

# Kenneth L Lay (POI)
# An outlier by any definition, but including him seems to improve accuracy
# del(data_dict['LAY KENNETH L'])

poi_list = [name for name in data_dict.keys() if data_dict[name]['poi']]
print('POI Count: {}\tNon-POI Count: {}'.format(
    len(poi_list), len(data_dict) - len(poi_list)))

### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.

# Consider the total volume of emails
for name in data_dict.keys():
    person = data_dict[name]
    if person['from_messages'] == 'NaN' or \
       person['to_messages'] == 'NaN':
        person['total_messages'] = 0

    else:
        person['total_messages'] = \
            person['from_messages'] + person['to_messages']

my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys=True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.2, random_state=36)

clf = AdaBoostClassifier(learning_rate=0.3, n_estimators=100, random_state=22)
# clf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
clf.fit(features_train, labels_train)

### Task 5: Tune your classifier to achieve better than .3 precision and recall
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info:
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

'''
Provides an overview of the most effective parameters for 
an AdaBoost classifier.
'''
def AdaParamTune():
    lr = [x/100.0 for x in range(10, 100, 20)]
    nr = [10, 30, 50, 100]
    acceptable = []

    # Takes x minutes
    for learn_r in lr:
        for ne in nr:
            print(str(learn_r) + ': ' + str(ne))
            clf = AdaBoostClassifier(learning_rate=learn_r, n_estimators=ne,
                                     random_state=22)
            scan = RFE(estimator=clf, n_features_to_select=5)
            scan.fit_transform(features_train, labels_train)

            new_feature_zip = zip(features_list[1:], scan.ranking_)
            new_features_list = ['poi'] + \
                                [tup[0] for tup in new_feature_zip if tup[1] == 1]
            pred = test_classifier(scan.estimator_, my_dataset, new_features_list)
            if pred[2] > 0.45:
                acceptable.append((pred, learn_r, ne))

    print(acceptable)


'''
Provides an overview of the most effective features using an RFE and
AdaBoost classifier.
'''
def FeatureSelectTune():
    f_size = len(features_list)
    results = []

    for i in range(f_size-1, 1, -1):
        print(i)
        clf = AdaBoostClassifier(learning_rate=0.3,
                                 n_estimators=100,
                                 random_state=22)
        scan = RFE(estimator=clf, n_features_to_select=i)
        scan.fit_transform(features_train, labels_train)

        new_feature_zip = zip(features_list[1:], scan.ranking_)
        new_features_list = ['poi'] + \
                            [tup[0] for tup in new_feature_zip if tup[1] == 1]

        pprint.pprint(new_features_list)
        clf = scan.estimator_
        pred = test_classifier(clf, my_dataset, new_features_list)
        if pred:
            results.append((i, pred[2]))

    if new_feature_zip:
        pprint.pprint(new_feature_zip)
    pprint.pprint(results)


# AdaParamTune()
FeatureSelectTune()

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.
#
# print('')
# print('Feature weights: ' + str(clf.feature_importances_))
# print(features_list)
#
# dump_classifier_and_data(clf, my_dataset, features_list)
