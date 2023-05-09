# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import numpy as np
import sklearn
from sklearn.ensemble import GradientBoostingClassifier
import pickle
import itertools
import sys, os
import time
import random

## usage) python3 collect.py programs_training.txt 20 1 training_data (use the pgms in 'pgms.txt', with k=10, trials=1)

training_data_folder = ""

if len(sys.argv) < 4:
    print("Insufficient arguments")
    exit(1)
elif len(sys.argv) == 4:
    filename = str(sys.argv[1])
    trials = 1
    training_data_folder = str(sys.argv[2])
    k = str(sys.argv[3])
else:
    print("Invalid arguments")
    exit(1)

if not os.path.isdir(f'./{training_data_folder}'):
    os.system(f'mkdir ./{training_data_folder}')

f = open(filename, "r")
pgms_str = f.read().replace('\n', ' ')
pgms = pgms_str.split()[:]
print(pgms)

random.seed()
pre_classifier = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=2)

def read_file(data_file):
    X, y = [], []
    with open(data_file, "r") as f:
        for line in f:
            data = list(map(lambda x: int(x), line.split()))
            fv = data[:len(data)-1]
            label = data[len(data)-1]
            X.append(fv)
            y.append(label)
    return X, y

def make_balance(X, y):
    lst = list(zip(X, y))
    pos = [(x,y) for (x,y) in lst if y == 1]
    neg = [(x,y) for (x,y) in lst if y == 0]
    #print(f'Original: #pos = {len(pos)}, #neg = {len(neg)}')
    assert (len(neg) >= len(pos))

    random.shuffle(neg)
    neg = neg[:len(pos)]

    #print(f'Balanced: #pos = {len(pos)}, #neg = {len(neg)}')
    pos.extend(neg)
    return zip(*pos)

def unique_sorted(values):
    "Return a sorted list of the given values, without duplicates."
    values = sorted(values)
    if not values:
        return []
    consecutive_pairs = zip(values, itertools.islice(values, 1, len(values)))
    result = [a for (a, b) in consecutive_pairs if a != b]
    result.append(values[-1])
    return result

def uniq(X, y):
    lst = list(zip(X, y))
    lst_uniq = unique_sorted(lst)
    print(f'before: {len(lst)}, uniq: {len(lst_uniq)}')
    return zip(*lst_uniq)

def preprocess(X, y):
    X, y = make_balance(X, y)
    return X, y

def trim_data(X, y, r):
    lst = list(zip(X, y))
    res = []
    for e in lst:
        if random.random() <= r:
            res.append(e)
    return zip(*res)

def train_clf (clf, X, y):
    X = np.array(X)
    y = np.array(y)
    clf.fit(X, y)
    return clf

def train_run(X, y, model_name):
    trained_clf = train_clf (pre_classifier, X, y)
    pickle.dump(trained_clf, open(model_name, "wb"))
    
def model(accum, model_path):
    train_X, train_y = read_file(accum)
    if (train_X == []):
        return
    train_X, train_y = preprocess(train_X, train_y)
    train_X, train_y = trim_data(train_X, train_y, 0.7)
    train_run(train_X, train_y, model_path)

mode = " --pulse-random-mode"
if os.path.isfile(f"./{training_data_folder}/acc.model"):
    #mode = f' --pulse-random-mode --pulse-cover-load history.txt'
    #mode = f' --pulse-join-train ./{training_data_folder}/acc.model --pulse-cover-load history.txt'
    mode = f' --pulse-join-train ./{training_data_folder}/acc.model --pulse-cover-load history.txt --pulse-repeat-mode'

def train(path, pgms, k):
    total_time = 0
    os.system(f'touch ./{training_data_folder}/accum.txt')
    for p in pgms:
        print(f"Training for {p}")
        infer_out = path + p
        if not os.path.isdir(infer_out):
            print("Error: infer-out does not exist for " + p)
            continue
        else:
            if os.path.isfile(f'./{training_data_folder}/{p}/history.dat'):
                os.system(f'mv ./{training_data_folder}/{p}/history.dat ./history.txt')
            start_t = time.time()
            cmd = ("infer analyze -j 1 --pulse-train-mode --pulse-only --pulse-max-disjuncts " + str(k) + " -o " + infer_out + " --pulse-cover-mode" + mode)

            print(cmd)
            os.system(cmd)

            end_t = time.time()
            elapsed_time = end_t - start_t

            if not os.path.isfile("./train.txt"):
                print("Error: train.txt does not exist for " + p)
                continue
            os.system(f'sort -u -r ./{training_data_folder}/accum.txt train.txt -o temp.txt') 
            os.system(f'mv temp.txt ./{training_data_folder}/accum.txt')
            r = random.randint(1,100000)
            if not os.path.isdir(f'./{training_data_folder}/{p}'):
                os.system(f'mkdir ./{training_data_folder}/{p}')
            os.system(f'mv train.txt ./{training_data_folder}/{p}/{r}.txt')
            os.system(f'mv history.txt ./{training_data_folder}/{p}/history.dat')

path = "/home/vagrant/infer-outs/"

train(path, pgms, k)
model(f'./{training_data_folder}/accum.txt', f'./{training_data_folder}/acc.model')
