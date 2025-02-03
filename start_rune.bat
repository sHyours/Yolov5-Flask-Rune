@echo off
cd /d %~dp0
py -3.9-64 app.py --device cpu --save 0  --port 5003 --model final
pause