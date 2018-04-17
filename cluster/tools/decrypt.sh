#!/bin/bash
if [ $# -lt 2 ]; then
  echo "$0 <private file> <in>"
else
    openssl rsautl -decrypt -inkey $1 -in $2
fi