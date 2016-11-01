#!/bin/bash

function quit_on_error() {
    test "0" = $? || {
        exit 1
    }
}

SERVICE_NAME=cloud4rpi.service
SCRIPT_PATH=$1
DIR=$(dirname "$0")

if [ ! -f "$SCRIPT_PATH" ] || [[ "$SCRIPT_PATH" != /* ]]; then
    echo "Usage: $0 /abs/path/to/the/script"
    echo "Invalid script path. Make sure it is absolute."
    exit 1
fi

echo "Generating init script..."
cat "$DIR/service.tmpl" | sed "s;%SCRIPT_PATH%;$SCRIPT_PATH;" > "$SERVICE_NAME"
echo "Done"

echo "Copying init script to /lib/systemd/system..."
cp "$SERVICE_NAME" "/lib/systemd/system/$SERVICE_NAME"
quit_on_error
echo "Done"

echo "Setting permissions..."
chmod +x "$SCRIPT_PATH"
chmod 644 "/lib/systemd/system/$SERVICE_NAME"
echo "Done"

echo "Configure systemd..."
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
quit_on_error
echo "Done"

echo "Usage example:"
echo -e "  $ sudo systemctl start|stop|status \e[0m$SERVICE_NAME\e[1m"
