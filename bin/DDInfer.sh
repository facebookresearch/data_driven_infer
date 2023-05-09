#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

model=""
if [ ! -d /vagrant/bin ];then
	echo "Vagrant is not detected. Please follow the instruction in README.md and run `vagrant ssh` first."
	exit 1
fi

if [ -d /vagrant/best_models ];then
	model="/vagrant/best_models"
elif [ -d /vagrant/Table2/trained_models ];then
	model="/vagrant/Table2/trained_models"
else
	echo "Cannot find a trained model. Please follow the instruction in Table2/README.md"
	exit 1
fi

python /vagrant/bin/DDInfer.py $model $1
