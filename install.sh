#!/bin/bash

BASEDIR=$(dirname $0)
SERVICE_NAME=cloud4rpi

echo "Installing cloud4rpi service..."

echo "Preparing Init-script from ${BASEDIR}"
python $BASEDIR/init_script_gen.py

echo "Copying Init-script to /etc/init.d"
sudo cp $BASEDIR/$SERVICE_NAME /etc/init.d/$SERVICE_NAME

echo "Set permissions of files"
sudo chmod 755 /etc/init.d/$SERVICE_NAME
sudo chmod 755 $BASEDIR/cloud4rpid.py

echo "Updating rc.d"
sudo update-rc.d $SERVICE_NAME defaults

echo "Cloud4RPI service successfully installed!"
echo -e "Please see the \e[1mcloud4rpid.log \e[0mfile in the /var/log/ directory to get logging information."
echo "Usage example:"
echo -e "$ sudo service \e[1mcloud4rpi \e[0mstart|stop|status"
