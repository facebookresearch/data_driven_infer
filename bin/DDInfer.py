# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import sys, os
import time
import re

mode="analyze"
m=3
pre_k=1
main_k=5

def run_infer(infer_out, k, model, quiet):
   total_time, total_alarms = 0, 0
   try:
       if not os.path.isdir(infer_out):
           print(f'  * Error: infer-out does not exist for {infer_out}')
           exit(1)
       else:
           start_t = time.time()
           use_model = f'--pulse-join-select {model}'

           threads = "-j 1"
           threads = ""

           verbose_opt = ""
           if quiet:
               verbose_opt = " -q 2>&1 > /dev/null"

           cmd = f'infer analyze {threads} --pulse-only --pulse-max-disjuncts {str(k)} -o {infer_out} {use_model} {verbose_opt}'
           print(f"    - cmd: {cmd}", file=sys.stderr)
           os.system(cmd)
           end_t = time.time()
           elapsed_time = end_t - start_t

           report = os.path.join(infer_out, "report.txt")
           f = open (report, "r")
           text = f.read().replace('\n', '')
           issues = re.findall('Found ([0-9]+) issue', text)
           if len(issues) == 0:
               issues_count = 0
           else:
               issues_count = int(issues[0])

           total_time = total_time + elapsed_time
           total_alarms = total_alarms + issues_count

       return total_time, total_alarms
   except:
       print(f"Skipping {p} due to unknown exceptions")
       return 0, 0
def run_infer_pre(path, k, model, quiet):
    return run_infer(path, k, model, quiet)
def run_infer_main(path, k, model, quiet):
    return run_infer(path, k, model, quiet)
def pre_analysis(pgm, pre_k, models):
    opt_model = None
    opt_alarms = -1
    pt = 0
    if len(models) == 1:
        return models[0], 0, 0
    for model in models:
        print(f"    * Pre-analysis with model {model}")
        t, a = run_infer_pre(pgm, pre_k, model, True)
        print(f"    # time(sec): {t}")
        print(f"    # alarms(#): {a}")
        if opt_alarms < a:
            opt_alarms = a
            opt_model = model
        pt = pt + t
    return opt_model, opt_alarms, pt

def run_dd_infer(path, pre_k, main_k, models):
    print("* Pre-analysis")
    model, alarms, pretime = pre_analysis(path, pre_k, models)
    print(f"# total pre-time(sec): {pretime}")
    print("* Main analysis")
    maintime, mainalarms = run_infer_main(path, main_k, model, False)
    print(f"# Main analysis time(sec): {maintime}")
    print(f"# alarms(#): {mainalarms}")

def main(target_path, model_path):
    files = os.listdir(f'{model_path}/{m}')
    pattern = ".*\.model"
    models = [f'{model_path}/{m}/{s}' for s in files if re.match(pattern, s)]
    print(f"prek = {pre_k}, maink = {main_k}, models = {models}", flush=True)
    run_dd_infer(target_path, pre_k, main_k, models)

def usage():
    print("usage:")
    print("python DDInfer.py ~/best_models ~/infer-outs/gawk-5.1.0")

if len(sys.argv) < 2:
    usage()
    exit(1)

model_path = sys.argv[1]
target_path = sys.argv[2]

if not os.path.isdir(model_path):
    print(f'Cannot find a model in {model_path}')
    usage()
    exit(1)

if not os.path.isdir(target_path):
    print(f'Cannot find a captured target in {target_path}')
    usage()
    exit(1)

main(target_path, model_path)

