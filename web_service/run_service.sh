#!/usr/bin/env sh

# swithc to the frontend dir, and start dev server
cd frontend && npm run dev &

# set up Flask APP
cd backend && python3 app.py
