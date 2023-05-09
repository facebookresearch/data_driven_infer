#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

if [ -d ./trained_models ];then
	echo "The preparation is already done. Run \`run.sh\` to evaluate the trained model."
	exit
fi

if [ ! -d ./merged_training_data ];then
	# Merge training data: `training_data` => `merged_training_data`
	path="training_data"
	mkdir merged_training_data
	pushd $path
	for v in `ls -d */`;do
	       echo ${v::-1};
	       cat ${v}*.txt | sort -u > ../merged_training_data/${v::-1}.merged.txt
        done
	popd
fi

# Generate trained model: `trained_models/*`
python bin/learn_classifier.py trained_models 1 1 bin/programs_train.txt

