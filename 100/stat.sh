#!/bin/bash

i=0
while [ $i -lt 206 ]
do
  echo
  echo f$i.bin
  echo
  python createVariationalSeriesGRD.py "/home/egor/Programs/Result/FI/f$i.bin"
  echo Done
  echo
  i=$(($i + 1))
done






