#!/bin/bash

target=$1

while true; do
	ike-scan -M --timeout 1 --sport 0 --retry 1 \
		--trans  "(3=65201,1=65532,2=65532,4=65201,11=1,12=0x00007080)" \
		--vendor cc6b10795140d8128aa586951bf37f1f000000020401455e020203010000000000000f79 \
		--vendor 09002689dfd6b712 --vendor 12f5f28c457168a9702d9fe274cc0100 \
		--vendor afcad71368a1f1c96b8696fc77570100 --vendor 90cb80913ebb696e086381b5ec427b1f \
		--vendor 7d9419a65310ca6f2c179d9215529d56  \
		--vendor 4048b7d56ebce88525e7de7f00d6c2d380000000 \
		--vendor f3cd10ffb2db8d350201ee010c53a0d1 \
		--vendor fee932efe10215f9ad3c3ce5938a5d79 $target
	 sleep 0.05 
done
