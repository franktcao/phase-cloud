#!/bin/bash

echo "Make sure you login first with"
echo ">>> heroku login"
if [ $# -eq 0 ]
  then
    git push heroku main
  else
    git push heroku $1
fi