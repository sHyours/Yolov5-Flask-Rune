@echo off
cd /d  %~dp0
py -3.9-64 app.py --device cpu --save 0 --port 5004 --model checker --thres 0.7 --log 1
pause