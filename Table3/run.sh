#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

OriginalInferTable="../Table1/data"
DDInferTable="../Table2/data"

if [ ! -d "${OriginalInferTable}" ];then
	echo "The original infer result is missing. Please run the experiment in 'Table1' folder.";
	exit 1
fi
if [ ! -d "${DDInferTable}" ];then
	echo "The data-driven infer result is missing. Please run the experiment in 'Table2' folder.";
	exit 1
fi

cnt=0
OUT="$(mktemp)"
tot=$(wc -l list | cut -f1 -d' ')
ith=0

(echo "Name |A| |B| |A\\B| |B\\A| |A&B| common(A,B) sim(A,B)";
echo "-------------- ---- ---- ----- ----- ----- -------- --------";
for v in `cat list`;do
	ith=$(($ith+1))
	>&2 printf " Processing ${v} (${ith}/${tot})                     \r"
	echo -n "$v "
	node ../bin/alarms.js -s -e -fm "${OriginalInferTable}/${v}_60.json" "${DDInferTable}/${v}_3_3_10.json"
	sim=$(node ../bin/alarms.js -a -s -fm "${OriginalInferTable}/${v}_60.json" "${DDInferTable}/${v}_3_3_10.json")
	printf " %.2f\n" $sim
done) | cut -f1,2,3,4,5,6,7,8 -d" " > $OUT


cp README.init README.md

echo "" >> README.md
echo "\`\`\`" >> README.md
(cat $OUT
echo "-------------- ---- ---- ----- ----- ----- -------- ---------";
echo -n "Total "
tail -n +3 $OUT | awk '{aa+=$2;bb+=$3;ab+=$4;ba+=$5;cc+=$6;com+=$7;sim+=$8;cnt++} END{printf "%d %d %d %d %d %.2f %.2f\n", aa,bb,ab,ba,cc,com/cnt,sim/cnt}') | column -t >> README.md
echo "\`\`\`" >> README.md

rm $OUT
cat README.md
