# Copyright (c) Meta Platforms, Inc. and affiliates
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
import sys, os
import time
import re
import random
from multiprocessing import Process, Queue, Manager

def split_list(a, n):
    k, m = divmod(len(a), n)
    return list(a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def run_random_infer(path, p, k, quiet):
   total_time, total_alarms = 0, 0
   try:
       infer_out = path + p
       if not os.path.isdir(infer_out):
           print("  * Error: infer-out does not exist for " + p)
           exit(1)
       else:
           start_t = time.time()

           if quiet:
               verbose_opt = " 2>&1 > /dev/null"

           os.system("infer analyze -q -j 1 --pulse-random-mode --pulse-only --pulse-max-disjuncts " + str(k) + " -o " + infer_out + " --pulse-cg-load " + "/vagrant/cgs/" + p + " " + verbose_opt)
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

           total_time = total_time + elapsed_time
           total_alarms = total_alarms + issues_count

       return total_time, total_alarms
   except:
       print(f"Skipping {p} due to unkonwn exceptions")
       return 0, 0

def run_infer(path, p, k, model, quiet, limit_fn, threads=1):
   total_time, total_alarms = 0, 0
   try:
       infer_out = os.path.join(path, p)
       if not os.path.isdir(infer_out):
           print("  * Error: infer-out does not exist for " + infer_out)
           exit(1)
       else:
           start_t = time.time()
           use_model = ""
           if model != None:
               use_model = "--pulse-join-select " + model

           limit_functions = ""
           if limit_fn != 0:
               limit_functions = " --pulse-limit-fn " + str(limit_fn) + " "

           verbose_opt = ""
           if quiet:
               verbose_opt = " 2>&1 > /dev/null"

           print(p, model)
           cmd = f"infer analyze -q -j {threads} --pulse-only --pulse-max-disjuncts " + str(k) + " -o " + infer_out + " " + use_model + limit_functions + verbose_opt
           print(cmd, file=sys.stderr)
           os.system(cmd)
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

           total_time = total_time + elapsed_time
           total_alarms = total_alarms + issues_count

       return total_time, total_alarms
   except:
       print(f"Skipping {p} due to unkonwn exceptions")
       return 0, 0


def run_infer_main(path, p, k, model, quiet, threads=1):
    return run_infer(path, p, k, model, quiet, 0, threads=threads)

def run_infer_pre(path, p, k, model, quiet, limit_fn, threads=1):
    return run_infer(path, p, k, model, quiet, limit_fn, threads=threads)

def work(path, pgms, k, model, quiet, return_dict):
    for pgm in pgms:
        t, a = run_infer_main(path, pgm, k, model, quiet)
        return_dict[pgm] = (a, t)

def run_infer_parallel(path, pgms, k, model, ncpus, quiet):
    pgms_orig = pgms[:]
    random.shuffle(pgms)
    splits = split_list(pgms, ncpus)
    for i in range(ncpus):
        print(f'cpu {i}: {splits[i]}', flush=True)

    manager = Manager()
    return_dict = manager.dict()
    jobs = []
    for i in range(ncpus):
        th = Process(target=work, args=(path, splits[i], k, model, quiet, return_dict))
        jobs.append(th)
        th.start()

    for job in jobs:
        job.join()

    t_sum, a_sum = 0, 0
    for pgm in return_dict:
        a, t = return_dict[pgm]
        t_sum = t_sum + t
        a_sum = a_sum + a

    for pgm in pgms_orig:
        a, t = return_dict[pgm]
        print(f'** {pgm}\t\t{a}\t\t{t}', flush=True)

    return t_sum, a_sum

def pre_analysis(path, pgm, pre_k, models, threads=1):
    opt_model = None
    opt_alarms = -1
    pt = 0
    if len(models) == 1:
        return models[0], 0, 0
    for model in models:
        t, a = run_infer_pre(path, pgm, pre_k, model, True, 0, threads=threads)
        if opt_alarms < a:
            opt_alarms = a
            opt_model = model
        pt = pt + t
    return opt_model, opt_alarms, pt

def work_dd(path, pgms, pre_k, main_k, models, quiet, threads, return_dict):
    for pgm in pgms:
        model, alarms, pretime = pre_analysis(path, pgm, pre_k, models, threads=threads)
        t, a = run_infer_main(path, pgm, main_k, model, quiet, threads=threads)
        infer_out = os.path.join(path, pgm)
        os.system(f"cp {infer_out}/report.json ./data/{pgm}_3_{pre_k}_{main_k}.json")
        return_dict[pgm] = (a, t, pretime)

def run_dd_infer_parallel(path, pgms, pre_k, main_k, models, ncpus, quiet, threads=1):
    pgms_orig = pgms[:]
    random.shuffle(pgms)
    splits = split_list(pgms, ncpus)
    for i in range(ncpus):
        print(f'cpu {i}: {splits[i]}', flush=True)

    manager = Manager()
    return_dict = manager.dict()
    jobs = []
    for i in range(ncpus):
        th = Process(target=work_dd, args=(path, splits[i], pre_k, main_k, models, quiet, threads, return_dict))
        jobs.append(th)
        th.start()

    for job in jobs:
        job.join()

    t_sum, pret_sum, a_sum = 0, 0, 0
    for pgm in return_dict:
        a, t, pret = return_dict[pgm]
        t_sum = t_sum + t
        a_sum = a_sum + a
        pret_sum = pret_sum + pret

    for pgm in pgms_orig:
        a, t, pret = return_dict[pgm]
        print(f'** {pgm}\t{a}\t{t}\t{pret}\t{pret+t}', flush=True)

    return t_sum, pret_sum, a_sum

def work_random(path, pgms, k, quiet, return_dict):
    for pgm in pgms:
        t, a = run_random_infer(path, pgm, k, quiet)
        return_dict[pgm] = (a, t)

def run_random_infer_parallel(path, pgms, k, ncpus, quiet):
    pgms_orig = pgms[:]
    random.shuffle(pgms)
    splits = split_list(pgms, ncpus)
    for i in range(ncpus):
        print(f'cpu {i}: {splits[i]}', flush=True)

    manager = Manager()
    return_dict = manager.dict()
    jobs = []
    for i in range(ncpus):
        th = Process(target=work_random, args=(path, splits[i], k, quiet, return_dict))
        jobs.append(th)
        th.start()

    for job in jobs:
        job.join()

    t_sum, a_sum = 0, 0
    for pgm in return_dict:
        a, t = return_dict[pgm]
        t_sum = t_sum + t
        a_sum = a_sum + a

    for pgm in pgms_orig:
        a, t = return_dict[pgm]
        print(f'** {pgm}\t\t{a}\t\t{t}', flush=True)

    return t_sum, a_sum


