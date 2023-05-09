#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

if [ ! -d ./trained_models ];then
	echo "Cannot find the \`trained_models\`. Run \`prepare.sh\` first."
	exit 1
fi

# Run the analysis with trained_models
rm -rf logs
mkdir logs

rm -rf data
mkdir data

M=1;K=5;./bin/eval.sh $K ./trained_models/$M | tee logs/M${M}_${K}_best.txt
M=1;K=20;./bin/eval.sh $K ./trained_models/$M | tee logs/M${M}_${K}_best.txt
M=3;K_pre=1;K_main=5;./bin/eval_ml_infer_with_pre.sh ${K_pre} ${K_main} ./trained_models/$M | tee logs/M${M}_${K_pre}_${K_main}_best.txt
M=3;K_pre=3;K_main=5;./bin/eval_ml_infer_with_pre.sh ${K_pre} ${K_main} ./trained_models/$M | tee logs/M${M}_${K_pre}_${K_main}_best.txt
M=3;K_pre=3;K_main=10;./bin/eval_ml_infer_with_pre.sh ${K_pre} ${K_main} ./trained_models/$M | tee logs/M${M}_${K_pre}_${K_main}_best.txt

