workon cv
cd ~/graduation_project/control
python control.py &
cd ../server
node server.js &
cd ../camera
python scheduler.py &
