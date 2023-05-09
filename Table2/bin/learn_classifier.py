# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import numpy as np
from multiprocessing import Process
import sklearn
from sklearn.ensemble import GradientBoostingClassifier
import sys
import random
import time
import pickle
import os
import itertools
from os.path import exists
from infer import *

random.seed()

#m0 |-> GradientBoostingClassifier(learning_rate=0.01, max_depth=1)
#m1 |-> GradientBoostingClassifier(learning_rate=0.01, max_depth=2)
#m2 |-> GradientBoostingClassifier(learning_rate=0.01, max_depth=4)
#m3 |-> GradientBoostingClassifier(max_depth=1)
#m4 |-> GradientBoostingClassifier(max_depth=2)
#m5 |-> GradientBoostingClassifier(max_depth=4)
#m6 |-> GradientBoostingClassifier(learning_rate=1.0, max_depth=1)
#m7 |-> GradientBoostingClassifier(learning_rate=1.0, max_depth=2)
#m8 |-> GradientBoostingClassifier(learning_rate=1.0, max_depth=4)
#m9 |-> GradientBoostingClassifier(learning_rate=0.01, max_depth=1, n_estimators=200)
#m10 |-> GradientBoostingClassifier(learning_rate=0.01, max_depth=2, n_estimators=200)
#m11 |-> GradientBoostingClassifier(learning_rate=0.01, max_depth=4, n_estimators=200)
#m12 |-> GradientBoostingClassifier(max_depth=1, n_estimators=200)
#m13 |-> GradientBoostingClassifier(max_depth=2, n_estimators=200)
#m14 |-> GradientBoostingClassifier(max_depth=4, n_estimators=200)
#m15 |-> GradientBoostingClassifier(learning_rate=1.0, max_depth=1, n_estimators=200)
#m16 |-> GradientBoostingClassifier(learning_rate=1.0, max_depth=2, n_estimators=200)
#m17 |-> GradientBoostingClassifier(learning_rate=1.0, max_depth=4, n_estimators=200)

classifiers = [GradientBoostingClassifier(n_estimators=ns, learning_rate=lr, max_depth=md)
                for ns in [100, 200]
                    for lr in [0.01, 0.1, 1.0]
                        for md in [1, 2, 4]]

classifiers = list(zip (range(len(classifiers)), classifiers))

for idx, clf in classifiers:
    print(f'm{idx} |-> {clf}')

def get_model_filename (folder, model_id):
    filename = folder + "/" + str(model_id) + ".model"
    return filename

def train_and_save (model_id, clf, X, y, folder):
    filename = get_model_filename (folder, model_id)
    if exists(filename):
        print(f'Skip training {model_id} {clf}: model already exists in {filename}')
    else:
        start_t = time.time()
        trained_clf = train_clf (clf, X, y)
        end_t = time.time()
        print(f'Training {model_id} {clf} finishes in {end_t-start_t} seconds', flush=True)
        pickle.dump(trained_clf, open(filename, "wb"))
    return

def split_list(a, n):
    k, m = divmod(len(a), n)
    return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def train_and_save_models (classifiers, X, y, folder):
    for model_id, clf in classifiers:
        train_and_save (model_id, clf, X, y, folder)

def train_parallel (classifiers, X, y, folder, cpus):
    clfs = classifiers[:]
    random.shuffle(clfs)
    splits = split_list(clfs, cpus)
    i = 0
    for split in splits:
        i = i + 1
        print(f'CPU {i} : {split}')
    jobs = []
    for i in range(cpus):
       th = Process(target=train_and_save_models, args=(splits[i], X, y, folder))
       jobs.append(th)

    for i in range(cpus):
        jobs[i].start()

    for i in range(cpus):
        jobs[i].join()

def get_pgm_name(fullpath):
    basename = os.path.basename(fullpath)
    assert (basename.endswith(".merged.txt"))
    return basename[:-11]

def unique_sorted(values):
    "Return a sorted list of the given values, without duplicates."
    values = sorted(values)
    if not values:
        return []
    consecutive_pairs = zip(values, itertools.islice(values, 1, len(values)))
    result = [a for (a, b) in consecutive_pairs if a != b]
    result.append(values[-1])
    return result

def train_clf (clf, X, y):
    X = np.array(X)
    y = np.array(y)
    clf.fit(X, y)
    return clf

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

def read_files(data_files):
    X, y = [], []
    for data_file in data_files:
        _X, _y = read_file(data_file)
        X.extend(_X)
        y.extend(_y)
    return X, y

def get_pos_neg(X, y):
    lst = list(zip(X, y))
    pos = [(x,y) for (x,y) in lst if y == 1]
    neg = [(x,y) for (x,y) in lst if y == 0]
    return pos, neg

def make_balance(X, y):
    lst = list(zip(X, y))
    pos = [(x,y) for (x,y) in lst if y == 1]
    neg = [(x,y) for (x,y) in lst if y == 0]
    assert (len(neg) >= len(pos))

    random.shuffle(neg)
    neg = neg[:len(pos)]

    pos.extend(neg)
    return zip(*pos)

def uniq(X, y):
    lst = list(zip(X, y))
    lst_uniq = unique_sorted(lst)
    print(f'before: {len(lst)}, uniq: {len(lst_uniq)}')
    return zip(*lst_uniq)

def preprocess(X, y):
    X, y = uniq(X, y)
    X, y = make_balance(X, y)
    return X, y

def trim_data(X, y, r):
    lst = list(zip(X, y))
    res = []
    for e in lst:
        if random.random() <= r:
            res.append(e)
    return zip(*res)

def get_train_data(train_files, ratio):
    train_X, train_y = read_files(train_files)
    assert (train_X != [])
    train_X, train_y = preprocess(train_X, train_y)
    pos, neg = get_pos_neg (train_X, train_y)
    print(f'#pos : {len(pos)}, #neg : {len(neg)}')
    train_X, train_y = trim_data(train_X, train_y, ratio)
    pos, neg = get_pos_neg (train_X, train_y)
    print(f'#pos : {len(pos)}, #neg : {len(neg)}')
    return train_X, train_y

def evaluate_clf_for_parallel(clf, valid_files, return_dict):
    for valid_file in valid_files:
        valid_X, valid_y = read_file(valid_file)
        try:
            valid_X, valid_y = make_balance(valid_X, valid_y)
        except:
            return_dict[valid_file] = (0, 0, 0, 0, 0)
            return
        predict_y = clf.predict(valid_X)

        pgm = get_pgm_name(valid_file)
        path = "/home/vagrant/infer-outs/"
        model = f"/tmp/model_tmp_{pgm}.model"
        if exists(model):
            os.system(f"rm {model}")
        pickle.dump(clf, open(model, "wb"))

        infer_time, infer_alarms = run_infer_main(path, pgm, 5, model, True)

        TP, FN, FP, TN = 0, 0, 0, 0
        for (gt, predict) in zip(valid_y, predict_y):
            if gt == 1:
                if predict == 1:
                    TP = TP + 1
                else:
                    FN = FN + 1
            else:
                if predict == 1:
                    FP = FP + 1
                else:
                    TN = TN + 1

        n_pos = sum(predict_y)
        n_neg = len(predict_y) - n_pos
        if TP + FN == 0:
            recall = -1
        else:
            recall = int(TP / (TP + FN) * 100)
        f1score = 0
        if TP + FP == 0:
            precision = -1
            f1score = 0
        else:
            precision = int(TP / (TP + FP) * 100)
            if precision + recall > 0:
                f1score = int(2 * recall * precision / (precision + recall))
            else:
                f1score = 0

        print(f'    - validation on {valid_file}', flush=True)
        print(f'      - predict: #pos={n_pos}, #neg={n_neg}')
        print(f'      - TP={TP}, FN={FN}, FP={FP}, TN={TN}')
        print(f'      - Recall={recall}, Precision={precision}, f1score={f1score}')
        print(f'      - Infer alarms={infer_alarms}, Infer time={infer_time}')
        return_dict[valid_file] = (TP, FN, FP, TN, infer_alarms)


def evaluate_clf_parallel(clf, valid_files, cpus):
    files = valid_files[:]
    random.shuffle(files)
    splits = split_list(files, cpus)
    print(splits)
    i = 0
    for split in splits:
        i = i + 1
        print(f'CPU {i} : {split}')
    jobs = []
    manager = Manager()
    return_dict = manager.dict()
    for i in range(cpus):
       th = Process(target=evaluate_clf_for_parallel, args=(clf, splits[i], return_dict))
       jobs.append(th)

    for i in range(cpus):
        jobs[i].start()

    for i in range(cpus):
        jobs[i].join()

    return return_dict

def report(header, TP, FN, FP, TN, IA):
    sensitivity = 0
    if TP + FN != 0:
        sensitivity = TP / (TP + FN)
    recall = sensitivity
    specitivity = 0
    if TN + FP != 0:
        specitivity = TN / (TN + FP)
    precision = 0
    if TP + FP != 0:
        precision = TP / (TP + FP)
    accuracy = 0
    if TP + FP + FN + TN != 0:
        accuracy = (TP + TN) / (TP + FP + FN + TN)
    f1score = 0
    if recall + precision != 0:
        f1score = 2 * (recall * precision) / (recall + precision)

    print()
    print("**********************************")
    print(header)
    print("**********************************")
    print(f'TP={TP}, FP={FP}, FN={FN}, TN={TN}')
    print("Sensitivity/Recall = TP / (TP + FN)            = %.2f" % sensitivity)
    print("Specificity        = TN / (TN + FP)            = %.2f" % specitivity)
    print("Precision          = TP / (TP + FP)            = %.2f" % precision)
    print("Accuracy           = (TP + TN) / (TP+FP+FN+TN) = %.2f" % accuracy)
    print("F1-score                                       = %.2f" % f1score)
    print("Infer alarms                                   = %d" % IA)
    print("**********************************")

def load_clf(clf_id, folder):
    model_file = get_model_filename (folder, clf_id)
    clf = pickle.load(open(model_file, 'rb'))
    return clf

def run_cv(data_files, folder_to_save_models, cpus, ratio_data, b_eval):
    train_files = data_files[:int(len(data_files)*0.7)]
    valid_files = [f for f in data_files if not f in train_files]
    print(f'training programs ({len(train_files)}) = {train_files}')
    print(f'validation programs ({len(valid_files)}) = {valid_files}')
    
    print(f'Processing training data', flush=True)
    start = time.time()
    train_X, train_y = get_train_data(train_files, ratio_data)
    end = time.time()
    print(f'Processing training data finishes in {end-start}s', flush=True)

    print(f'Training begins', flush=True)
    start = time.time()
    train_parallel(classifiers, train_X, train_y, folder_to_save_models, cpus)
    end = time.time()
    print(f'Training finished in {end-start} seconds', flush=True)

    result = []
    i = 0

    if b_eval == False:
        return result
    for clf_idx, clf in classifiers:
        i = i + 1
        TP, FN, FP, TN, IA = 0, 0, 0, 0, 0
        print()

        print(f'Evaluating {clf_idx} {clf}', flush=True)
        clf = load_clf(clf_idx, folder_to_save_models)

        log = {}
        log = evaluate_clf_parallel(clf, valid_files, cpus)

        result.append(((clf_idx, clf), log))
    return result

### use the result of Infer as metric
def clf_metric(TP, FN, FP, TN, IA):
    return IA

def alarms_of_model (pgms, m, M):
    s = 0
    for p in pgms:
        s = s + M[m][p]
    return s

def max_alarms (p, models, M):
    max = 0
    for m in models:
        if M[m][p] > max:
            max = M[m][p]
    return max

def sum_of_max_alarms (pgms, models, M):
    sum = 0
    for p in pgms:
        sum = sum + max_alarms (p, models, M)
    return sum

def best_model (pgms, models, M):
    max_alarms = 0
    max_model = None
    for m in models:
        alarms = alarms_of_model (pgms, m, M)
        if max_alarms < alarms:
            max_alarms = alarms
            max_model = m
    return max_model, max_alarms

def opt_model_comb (k, pgms, models, M):
    combs = list(itertools.combinations (models, k))
    opt_comb = None
    opt_alarms = 0
    for comb in combs:
        alarms = sum_of_max_alarms (pgms, comb, M)
        if opt_alarms < alarms:
            opt_alarms = alarms
            opt_comb = comb
    return opt_comb, opt_alarms

def select_models(result, folder_to_save_models):
    print()
    best_clf = None
    best_clf_metric = -1
    dic = {}
    for (clf_idx, clf),log in result:
        print(f'{clf_idx}. {clf}')
        TP, FN, FP, TN, IA = 0, 0, 0, 0, 0
        for pgm,(tp,fn,fp,tn,ia) in log.items():
            print(f'  - {pgm}: TP={tp}, FN={fn}, FP={fp}, TN={tn}, IA={ia}')
            TP, FN, FP, TN, IA = TP + tp, FN + fn, FP + fp, TN + tn, IA + ia
            subdic = dic.get(pgm, {})
            subdic[(clf_idx, clf)] = (tp, fn, fp, tn, ia)
            dic[pgm] = subdic

        if clf_metric(TP, FN, FP, TN, IA) > best_clf_metric:
            best_clf_metric = clf_metric(TP, FN, FP, TN, IA)
            best_clf = ((clf_idx, clf), TP, FN, FP, TN, IA)

        print()

    print("----------------------------------------------------")
    print("                Best model")
    print("----------------------------------------------------")
    (clf_idx, clf), TP, FN, FP, TN, IA = best_clf
    report(f"best clf : {clf_idx}. {clf}", TP, FN, FP, TN, IA)

    os.system("mkdir best_models")
    pickle.dump(clf, open("./best_models/best.model", "wb"))

    print("----------------------------------------------------")
    print("                Best models per program")
    print("----------------------------------------------------")
    best_alarms_sum = 0

    alarms = {}
    for pgm, subdic in dic.items():
        print(pgm)
        best_clf = None
        best_clf_metric = -1
        alarms[pgm] = {}
        for (clf_idx, clf), (TP, FN, FP, TN, IA) in subdic.items():
            alarms[pgm][clf_idx] = IA
            if clf_metric(TP, FN, FP, TN, IA) > best_clf_metric:
                best_clf_metric = clf_metric(TP, FN, FP, TN, IA)
                best_clf = ((clf_idx, clf), TP, FN, FP, TN, IA)

        (clf_idx, clf), TP, FN, FP, TN, IA = best_clf
        basename = os.path.basename(pgm)
        report(f'best clf for {basename} : {clf_idx} {clf}', TP, FN, FP, TN, IA)
        pickle.dump(clf, open(f"./best_models/{basename}.model", "wb"))
        best_alarms_sum = best_alarms_sum + IA
    print()
    print("----------------------------------------------------")
    print(f'#Alarms of optimal Infer: {best_alarms_sum}')
    print("----------------------------------------------------")

    M = {}
    pgms = []
    models = []
    for pgm in alarms:
        pgms.append(pgm)
    for (clf_id, _) in classifiers:
        models.append(clf_id)

    print(f'pgms  : {pgms}')
    print(f'models: {models}')

    for m in models:
        M[m] = {}
        for p in pgms:
            if p in alarms and m in alarms[p]:
                M[m][p] = alarms[p][m]
            else:
                M[m][p] = 0

    bm, ba = best_model (pgms, models, M)
    print("-----------------------------------")
    print(f'best model: {bm},  #alarms: {ba}')
    print("-----------------------------------")

    for k in range(1, 4):
        opt_comb, opt_alarms = opt_model_comb(k, pgms, models, M)
        print(f'comb size: {k}, optimal combination: {opt_comb},  #alarms: {opt_alarms}')

        folder =  folder_to_save_models + "/" + str(k)
        os.system("mkdir " + folder)
        for m in opt_comb:
            mfile = get_model_filename (folder_to_save_models, m)
            os.system("cp " + mfile + " " + folder)

    for pgm in alarms:
        for clf_idx in alarms[pgm]:
            basename = get_pgm_name(pgm)
            print(f'{basename} # m{clf_idx} # {alarms[pgm][clf_idx]}')

    for p in pgms:
        for m in models:
            print(f'M[{m}][{p}] : {M[m][p]}')


if len(sys.argv) < 3:
    print("Error: insufficient arguments")
    exit(1)

folder_to_save_models = sys.argv[1]
ratio_of_data_to_use = float(sys.argv[2])
num_of_cpus = int(sys.argv[3])
filename = sys.argv[4]
f = open(filename, "r")
pgms_str = f.read().replace('\n', ' ')
pgms = pgms_str.split()[:]
print(pgms)

data_files = []
for p in pgms:
    name="./merged_training_data/" + p + ".merged.txt"
    if exists(name):
        data_files.append(name)

if not exists(folder_to_save_models):
    os.system(f"mkdir {folder_to_save_models}")

b_eval = True
print(f'save models in {folder_to_save_models}, using {num_of_cpus} cpus')
result = run_cv(data_files, folder_to_save_models, num_of_cpus, ratio_of_data_to_use, b_eval)
if b_eval:
    select_models(result, folder_to_save_models)

