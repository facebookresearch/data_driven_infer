#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

K=$1
path=$2
for m in `ls $path`; do
    python bin/eval_ml_infer.py bin/programs_test.txt $path/$m $K
done

