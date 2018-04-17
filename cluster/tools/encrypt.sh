#!/bin/bash
if [ $# -lt 2 ]; then
  echo "$0 <publickey file> <in>"
else
    PUBLIC_KEY=$1
    openssl rsautl -encrypt -inkey ${PUBLIC_KEY} -pubin -in $2
fi