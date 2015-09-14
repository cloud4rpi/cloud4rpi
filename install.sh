#!/bin/sh

BASEDIR=$(dirname $0)
SERVICE_NAME=cloud4rpid.sh

echo "Installing Cloud4rpi daemon service..."

echo "Preparing Init-script from ${BASEDIR}"
python $BASEDIR/init_script_gen.py

echo "Copying Init-script to /etc/init.d"
sudo cp $BASEDIR/$SERVICE_NAME /etc/init.d/$SERVICE_NAME

echo "Set permissions of files"
sudo chmod 755 /etc/init.d/$SERVICE_NAME
sudo chmod 755 $BASEDIR/cloud4rpid.py

echo "Updating rc.d"
sudo update-rc.d $SERVICE_NAME defaults

echo "Please see the cloud4rpi.log file in the /var/log/ directory to get logging information."