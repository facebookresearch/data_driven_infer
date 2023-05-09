#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

timeout=10000
budget=1

timer() {
    declare -i c
    c=0
    while [ "$c" -lt "$1" ];do
        kill -0 $2 2> /dev/null
        if [ $? -eq 0 ];then
            c=$c+1
            sleep 1
        else
            echo "[ Success ]"
            exit
        fi
    done
    echo "[ Time out: over $1 sec ]"

    killtree $2 9
    exit
}

killtree() {
    local _pid=$1
    local _sig=${2-TERM}
    kill -stop ${_pid} 2> /dev/null
    for _child in $(ps ax -o "pid= ppid=" | awk "{ if ( \$2 == ${_pid} ) { print \$1 }}");do
        killtree ${_child} ${_sig}
    done
    kill -${_sig} ${_pid} 2> /dev/null
}

if [ -d ./trained_models ];then
	echo "The preparation is already done. Run \`run.sh\` to evaluate the trained model."
	exit
fi

echo "* Warning: The collection of training data takes an extremely long time (should run at least 7 days)."
echo "When the given time budget expires, manually halt this process and run the script \`finalize.sh\`."

# Generate training data: it creates `training_data` folder
for i in $(seq 1 $budget)
do
    for k in $(seq 1 4) # 40
    do
        {
    	    python bin/collect.py bin/programs_train.txt training_data $k
        } & pid=$!
        timer $timeout $pid & pid_timer=$!
        wait 2> /dev/null
        RETVAL=$?

        if [ $RETVAL -ne 0 ];then
            killtree $pid_timer 9
            wait 2> /dev/null
            killtree $pid 9
            wait 2> /dev/null
        fi
    done
done

