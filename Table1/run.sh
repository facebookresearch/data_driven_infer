#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

OUT_PATH="/home/vagrant/infer-outs"
TESTSET=(5 10 20 30 40 50 60)

run-single() {
	name="./data/$1_$2.json"
	if [ -f "$name" ]; then
		echo "$name exists."
	else
		start=`date +%s`
		rm -f $OUT_PATH/$1/report.json
		echo "- cmd: infer analyze -j 1 --pulse-only --pulse-max-disjuncts $2 -o \"$OUT_PATH/$1\""
		infer analyze -j 1 --pulse-only --pulse-max-disjuncts $2 -o "$OUT_PATH/$1"
		err=$?
		end=`date +%s`
		elapsed=$((end-start))
		if [ $err -eq 0 ];then
			cp $OUT_PATH/$1/report.json ${name}
			alarms=$(node /vagrant/bin/parse-result.js $OUT_PATH/$1/report.json)
			echo "$1 \"k = $2\" $alarms $elapsed " | tee -a result.log
		else
			echo "[\"exception\"]" > ${name}
			(echo "$1 \"k = $2\" err $elapsed") | tee -a result.log
		fi
	fi
}

[[ -d "./data" ]] || mkdir data

for t in ${TESTSET[@]}; do
	for v in `cat list`;do
		run-single $v $t
	done
done

