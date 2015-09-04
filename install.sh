#!/bin/sh

SERVICE_NAME=cloud4rpid.sh
SOURCE_DIR=$HOME/cloud4rpi
DEST_DIR=/etc/init.d

sudo chmod 755 $SOURCE_DIR/cloud4rpid.py

sudo cp $SOURCE_DIR/$SERVICE_NAME $DEST_DIR/$SERVICE_NAME
sudo chmod 755 $DEST_DIR/$SERVICE_NAME
sudo update-rc.d $SERVICE_NAME defaults

