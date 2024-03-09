#!/bin/bash

python -m main

git pull
git add klastro.atom
git commit -m "Update astronomical forecast"
git push origin master