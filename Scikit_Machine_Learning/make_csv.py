#!/usr/bin/python

import sys
import pickle
import csv
sys.path.append("../tools/")



### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file, open("enron.csv", "w+") as csvfile:
    data_dict = pickle.load(data_file)
    names = data_dict.keys()
    writ = csv.DictWriter(csvfile, fieldnames=data_dict[names[0]])
    writ.writeheader()
    for name in names:
        writ.writerow(data_dict[name])
