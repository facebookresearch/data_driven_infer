#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
# 
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

cp README.init README.md

grep "\*\* " logs/M1_5_best.txt | cut -f2- -d' ' | sort -k1 | awk '{printf "%s %d %.1f |\n", $1, $2, $3}' | column -t > t0
grep "\*\* " logs/M1_20_best.txt | cut -f2- -d' ' | sort -k1 | awk '{printf "%s %d %.1f |\n", $1, $2, $3}' | column -t > tmp
join -1 1 -2 1 t0 tmp > t;mv t t0
grep "\*\* " logs/M3_1_5_best.txt | cut -f2- -d' ' | sort -k1 | awk '{printf "%s %d %.1f %.1f %.1f |\n", $1, $2, $4, $3, $5}' | column -t > tmp
join -1 1 -2 1 t0 tmp > t;mv t t0
grep "\*\* " logs/M3_3_5_best.txt | cut -f2- -d' ' | sort -k1 | awk '{printf "%s %d %.1f %.1f %.1f |\n", $1, $2, $4, $3, $5}' | column -t > tmp
join -1 1 -2 1 t0 tmp > t;mv t t0
grep "\*\* " logs/M3_3_10_best.txt | cut -f2- -d' ' | sort -k1 | awk '{printf "%s %d %.1f %.1f %.1f |\n", $1, $2, $4, $3, $5}' | column -t > tmp
join -1 1 -2 1 t0 tmp > t;mv t tmp

cat tmp | awk '{s2=s2+$2;s3=s3+$3;s4=s4+$5;s5=s5+$6;s6=s6+$8;s7=s7+$9;s8=s8+$10;s9=s9+$11;s10=s10+$13;s11=s11+$14;s12=s12+$15;s13=s13+$16;s14=s14+$18;s15=s15+$19;s16=s16+$20;s17=s17+$21} END{print "Total",s2,s3,"|",s4,s5,"|",s6,s7,s8,s9,"|",s10,s11,s12,s13,"|",s14,s15,s16,s17}' > sum
repeat(){
	for j in {1..4};do
		echo -n "$1";
	done
}
bar(){
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	echo -n "| "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	echo -n "| "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	echo -n "| "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	echo -n "| "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	repeat $1;echo -n " "
	echo
}
echo "\`\`\`" >> README.md
echo "                    (M=1, K=5)          (M=1, K=20)                 (M=3, K_pre=1, K_main=5)                    (M=3, K_pre=3, K_main=5)                            (M=3, K_pre=3, K_main=10)" >> README.md
(bar "-";echo "name alarms(#) time(s) | alarms(#) time(s) | alarms(#) pre-time(s) main-time(s) time(s) | alarms(#) pre-time(s) main-time(s) time(s) | alarms(#) pre-time(s) main-time(s) time(s)";bar "-";cat tmp;bar "=";cat sum) | column -t >> README.md
echo "\`\`\`" >> README.md

rm t0 tmp sum

cat README.md

