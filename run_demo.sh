#!/usr/bin/env sh

# swithc to the frontend dir, and start dev server
cd front_demo && npm run dev &

# set up Flask APP
python app.py