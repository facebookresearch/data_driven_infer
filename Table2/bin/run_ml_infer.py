# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import sys, os
import infer

if len(sys.argv) < 6:
    print("usage:")
    print("python run_ml_infer.py bin/programs_test.txt 1 5 1 models")
    exit(1)

filename = sys.argv[1]
pre_k = int(sys.argv[2])
main_k = int(sys.argv[3])
ncpus = int(sys.argv[4])
models = []

for model in sys.argv[5:]:
    models.append(model)

path = "/home/vagrant/infer-outs/"
if os.path.exists(filename):
    txtfile = open(filename, "r")
    pgms = txtfile.read().splitlines()
else:
    pgms = [filename]

print(f"prek = {pre_k}, maink = {main_k}, models = {models}", flush=True)
t, pret, a = infer.run_dd_infer_parallel(path, pgms, pre_k, main_k, models, ncpus, True)

print(f"k: {pre_k} {main_k}, alarms: {a}, pre_time: {pret}, main_time: {t}, total_time: {t+pret}, with model: {models}", flush=True)
