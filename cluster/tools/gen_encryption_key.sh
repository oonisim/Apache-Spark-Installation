#!/bin/bash
openssl genrsa -out private.pem && chmod 0600 private.pem
openssl rsa -in private.pem -pubout -out public.pem

