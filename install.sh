#!/bin/bash

function quit_on_error() {
    test "0" = $? || {
        exit 1
    }
}

SERVICE_NAME=cloud4rpi.service

echo "Generating init script..."
cat ./tools/templates/service.tmpl | sed "s;%CLOUD4RPI_DIR%;$(pwd);" > $SERVICE_NAME
echo "Done"

echo "Copying init script to /lib/systemd/system..."
cp $SERVICE_NAME /lib/systemd/system/$SERVICE_NAME
quit_on_error
echo "Done"

echo "Setting permissions..."
chmod +x app.py
chmod 644 /lib/systemd/system/$SERVICE_NAME
echo "Done"

echo "Configure systemd..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
quit_on_error
echo "Done"

echo -e "Please see the \e[1mcloud4rpid.log \e[0mfile in the /var/log/ directory to get logging information."
echo "Usage example:"
echo -e "$ sudo systemctl \e[0mstart|stop|status \e[1mcloud4rpi.service"
