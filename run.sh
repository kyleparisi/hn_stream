#!/bin/bash

export $(cat .env | grep -v ^# | xargs);
exec python main.py
