#!/bin/bash

python -m main

git remote add origin https://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@github.com/ebour/klastro
git pull
git add klastro.atom
git commit -m "Update astronomical forecast"
git push origin master
