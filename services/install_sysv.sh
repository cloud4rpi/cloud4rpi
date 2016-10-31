#!/bin/bash

function quit_on_error() {
    test "0" = $? || {
        exit 1
    }
}

SERVICE_NAME=cloud4rpid
SCRIPT_PATH=$1
DIR=$(dirname "$0")

if [ ! -f "$SCRIPT_PATH" ] || [[ "$SCRIPT_PATH" != /* ]]; then
    echo "Usage: $0 /abs/path/to/the/script"
    echo "Invalid script path. Make sure it is absolute."
    exit 1
fi

echo "Generating init script..."
cat "$DIR/service_sysv.tmpl" | sed "s;%SCRIPT_PATH%;$SCRIPT_PATH;" > "$SERVICE_NAME"
echo "Done"

echo "Copying init script to /etc/init.d..."
cp "$SERVICE_NAME" "/etc/init.d/$SERVICE_NAME"
quit_on_error
echo "Done"

echo "Setting permissions..."
chmod +x "$SCRIPT_PATH"
chmod +x "/etc/init.d/$SERVICE_NAME"
echo "Done"

echo "Installing init script links..."
update-rc.d "$SERVICE_NAME" defaults
quit_on_error
echo "Done"

echo "Usage example:"
echo -e "  $ sudo service \e[1mcloud4rpi\e[0m start|stop|status"
