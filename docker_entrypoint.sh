#!/bin/bash

set -e

exec python3 scrapper/main.py &
exec python3 app/controller/app.py