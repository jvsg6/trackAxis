#!/bin/bash

i=81
while [ $i -lt 206 ]
do
  echo $(date +"%y-%m-%d %T")
  echo
  echo f$i.bin
  echo
  python trackAxis.py "/home/egor/Programs/Result/1.00/SI/f$i.grd"
  echo Done
  echo
  i=$(($i + 1))
done





