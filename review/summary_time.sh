#!/bin/bash
let sum=0;

for i in {1..10}; do
  time=`curl -o /dev/null -s -w "%{time_total}" http://localhost:8000/api/summary`
  echo "Request $i took $time seconds"
  sum=$(echo "$sum + $time" | bc)
done

avg=$(echo "scale=4; $sum / 10" | bc)
echo "Average: $avg seconds"