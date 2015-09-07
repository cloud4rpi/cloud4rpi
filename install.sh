#!/bin/sh

BASEDIR=$(dirname $0)
SERVICE_NAME=cloud4rpid.sh

echo "Prepare Init-script in ${BASEDIR}"
python $BASEDIR/init_script_patcher.py

echo "Copying Init-script into /etc/init.d"
sudo cp $BASEDIR/$SERVICE_NAME /etc/init.d/$SERVICE_NAME

echo "Copying Init-script into /etc/init.d"
sudo cp $BASEDIR/$SERVICE_NAME /etc/init.d/$SERVICE_NAME


echo "Set scripts permissions"
sudo chmod 755 /etc/init.d/$SERVICE_NAME
sudo chmod 755 $BASEDIR/cloud4rpid.py

echo "Updating rc.d"
sudo update-rc.d $SERVICE_NAME defaults