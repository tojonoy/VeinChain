#!/bin/bash
# Start the application
gunicorn -w 4 web3flas:app --bind 0.0.0.0:8000