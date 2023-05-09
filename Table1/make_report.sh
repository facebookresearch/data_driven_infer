#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

LOGFILE=result.log
LOCS=/vagrant/common/locs
get_loc() {
	if [ -f "$LOCS" ];then
		grep "$1 " $LOCS | cut -f2 -d' '
	else
		echo 0
	fi
}

cp README.init README.md
cat >> README.md << EOF

## Result Table

EOF

heads=$(grep -o "\"k = [0-9]*\"" $LOGFILE | sed -e 's/"//g' | sort -u -k3 -n)

(for v in `cat list`;do
	loc=$(get_loc $v)
	loc=$(printf "%'d" $loc)
	echo "$v | $loc |"
done) | sort | column -t > tmp
sum=("Total | - | ")
first=("Name | LOC |")
group=(". | . |")
split=("---------------- | --- |")

while IFS= read -r head; do
	first+=("alarms(#) time(s) |")
	split+=("--------- ------- |")
	hh=$(echo $head | sed -e "s/ //g")
	group+=("$hh . |")
	grep "\"$head\"" $LOGFILE | sed -e "s/\"$head\" //" | sed -e "s/$/ |/" | sort | column -t > t0
	total=$(cat t0 | awk '{s1=s1+$2;s2=s2+$3} END{ print s1,s2 }')
	sum+=("$total |")
	join -j 1 tmp t0 > t1;mv t1 tmp
done <<< "$heads"
rm -f t0

echo "\`\`\`" >> README.md
(echo ${group[@]};echo ${split[@]};echo ${first[@]};echo ${split[@]};cat tmp;echo ${split[@]};echo ${sum[@]}) | column -t >> README.md
echo "\`\`\`" >> README.md
rm -f tmp

cat README.md
