#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

prek=$1
maink=$2
path=$3

for pgm in `cat bin/programs_test.txt`; do
    python bin/run_ml_infer.py $pgm $prek $maink 1 $path/*.model
done
