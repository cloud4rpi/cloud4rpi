#!/bin/sh

BASEDIR=$(dirname $0)
SERVICE_NAME=cloud4rpid.sh

echo "Preparing Init-script from ${BASEDIR}"
python $BASEDIR/init_script_patcher.py

echo "Copying Init-script into /etc/init.d"
sudo cp $BASEDIR/$SERVICE_NAME /etc/init.d/$SERVICE_NAME

echo "Set scripts permissions"
sudo chmod 755 /etc/init.d/$SERVICE_NAME
sudo chmod 755 $BASEDIR/cloud4rpid.py

echo "Validating unix newline strings"
sudo apt-get install dos2unix
sudo dos2unix $BASEDIR/cloud4rpid.py

echo "Updating rc.d"
sudo update-rc.d $SERVICE_NAME defaults
