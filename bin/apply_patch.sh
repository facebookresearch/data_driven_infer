#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
 
pushd infer
git checkout 3df3ca9eacdf2e7a697b69a716896bbee7419a7a
git am ../patches/0001-ddinfer-Data-driven-Infer-Initial-commit.patch
popd
