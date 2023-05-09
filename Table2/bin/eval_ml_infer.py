# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import sys, os
import time
import re

def run(path, p, k, model):
    total_time, total_alarms = 0, 0
    try:
        infer_out = path + p
        if not os.path.isdir(infer_out):
            print("  * Error: infer-out does not exist for " + p)
            exit(1)
        else:
            start_t = time.time()
            use_model = ""
            if model != None:
                use_model = "--pulse-join-select " + model
            os.system("infer analyze -q -j 1 --pulse-only --pulse-max-disjuncts " + str(k) + " -o " + infer_out + " " + use_model)
            end_t = time.time()
            elapsed_time = end_t - start_t

            report = path + p + "/report.txt"
            f = open (report, "r")
            text = f.read().replace('\n', '')
            issues = re.findall('Found ([0-9]+) issue', text)
            if len(issues) == 0:
                issues_count = 0
            else:
                issues_count = int(issues[0])

            os.system(f"cp {infer_out}/report.json ./data/{p}_1_{k}.json")

            total_time = total_time + elapsed_time
            total_alarms = total_alarms + issues_count

        return total_time, total_alarms
    except:
        print(f"Skipping {p} due to unkonwn exceptions")
        return 0, 0

pgm = None
k = 10
model = None
filename = None

if len(sys.argv) < 4:
    print("Insufficient arguments")
    exit(1)
elif len(sys.argv) == 4:
    filename = sys.argv[1]
    model = sys.argv[2]
    k = sys.argv[3]
else:
    print("Invalid arguments")
    exit(1)

path = "/home/vagrant/infer-outs/"

f = open(filename, "r")
pgms_str = f.read().replace('\n', ' ')
pgms = pgms_str.split()[:]

for pgm in pgms:
    t0, a0 = run(path, pgm, k, model)
    print(f'** {pgm}\t{a0}\t{t0}')
