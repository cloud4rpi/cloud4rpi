#!/bin/bash

function quit_on_error() {
    test "0" = $? || {
        exit 1
    }
}

SERVICE_NAME=cloud4rpi

echo "Generating init script..."
cat ./cloud4rpi.tmpl | sed "s;%CLOUD4RPI_DIR%;$(pwd);" > $SERVICE_NAME
echo "Done"

echo "Setting permissions..."
chmod +x ./cloud4rpi
echo "Done"

echo "Copying init script to /etc/init.d..."
cp $SERVICE_NAME /etc/init.d/$SERVICE_NAME
quit_on_error
echo "Done"

echo "Installing init script links..."
update-rc.d $SERVICE_NAME defaults
quit_on_error
echo "Done"

echo -e "Please see the \e[1mcloud4rpid.log \e[0mfile in the /var/log/ directory to get logging information."
echo "Usage example:"
echo -e "$ sudo service \e[1mcloud4rpi \e[0mstart|stop|status"
