#!/bin/bash

quit_on_error() {
    test "0" = $? || {
        exit 1
    }
}

systemd_script(){
    cat <<'EOF'
[Unit]
Description=Cloud4RPi daemon
After=network.target

[Service]
Type=idle
ExecStart=/usr/bin/python %SCRIPT_PATH%

[Install]
WantedBy=multi-user.target
EOF
}

systemv_script(){
    cat <<'EOF'
#!/bin/sh

### BEGIN INIT INFO
# Provides:          cloud4rpi
# Required-Start:    $local_fs $network $named $time $syslog
# Required-Stop:     $local_fs $network $named $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Cloud4RPi demon
# Description:       Cloud4RPi demon working with
#                    Raspberry Pi GPIO from Python
### END INIT INFO

SCRIPT=%SCRIPT_PATH%
RUNAS=root

PIDFILE=/var/run/cloud4rpi.pid
LOGFILE=/var/log/cloud4rpi.log

start() {
  if is_running; then
    echo 'Service already running' >&2
    return 1
  fi
  echo 'Starting service…' >&2
  local CMD="$SCRIPT &> \"$LOGFILE\" & echo \$!"
  su -c "$CMD" $RUNAS > "$PIDFILE"
  echo 'Service started' >&2
}

stop() {
  if ! is_running; then
    echo 'Service not running' >&2
    return 1
  fi
  echo 'Stopping service…' >&2
  kill -15 `get_pid` && rm -f "$PIDFILE"
  echo 'Service stopped' >&2
}

uninstall() {
  echo -n "Are you really sure you want to uninstall this service? That cannot be undone. [yes|No] "
  local SURE
  read SURE
  if [ "$SURE" = "yes" ]; then
    stop
    rm -f "$PIDFILE"
    echo "Notice: log file is not be removed: '$LOGFILE'" >&2
    update-rc.d -f cloud4rpi remove
    rm -fv "$0"
  fi
}

get_pid() {
    cat "$PIDFILE"
}

is_running() {
    [ -f "$PIDFILE" ] && ps `get_pid` > /dev/null 2>&1
}

case "$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  uninstall)
    uninstall
    ;;
  retart)
    stop
    start
    ;;
  status)
    if is_running; then
        echo "Running"
    else
        echo "Stopped"
        exit 1
    fi
    ;;
  *)
    echo "Usage: $0 {start|stop|status|restart|uninstall}"
esac
EOF
}

put_script(){
    echo "Moving init script into $1..."
    mv "$2" "$1/$2"
    quit_on_error
    echo "Setting permissions..."
    chmod 644 "$1/$2"
    quit_on_error
}

install_sysv() {
    SERVICE_NAME=cloud4rpid
    SYSTEMV_DIR=/etc/init.d

    echo "Generating init script..."
    systemv_script | sed "s;%SCRIPT_PATH%;$SCRIPT_PATH;" > "$SERVICE_NAME"

    put_script $SYSTEMV_DIR $SERVICE_NAME

    echo "Installing init script links..."
    update-rc.d "$SERVICE_NAME" defaults
    quit_on_error

    echo "All done!"
    echo "Usage example:"
    echo -e "  $ sudo service \e[1m$SERVICE_NAME\e[0m start|stop|status"
}

install_sysd() {
    SERVICE_NAME=cloud4rpi.service
    SYSTEMD_DIR=/lib/systemd/system

    echo "Generating init script..."
    systemd_script | sed "s;%SCRIPT_PATH%;$SCRIPT_PATH;" > "$SERVICE_NAME"

    put_script $SCRIPT_PATH $SYSTEMD_DIR $SERVICE_NAME

    echo "Configuring systemd..."
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    quit_on_error

    echo "All done!"
    echo "Usage example:"
    echo -e "  $ sudo systemctl start|stop|status \e[0m$SERVICE_NAME\e[1m"
}

SCRIPT_PATH=$(readlink -f "$1")
DIR=$(dirname "$0")

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Usage: $0 path/to/the/script"
    echo "Invalid script path. Make sure it exists."
    exit 1
fi

chmod +x "$SCRIPT_PATH"
quit_on_error

case $(ps -p 1 -o comm=) in
    "init") install_sysv ;;
    "systemd") install_sysd ;;
    *)
        echo "Unfortunately we can\'t automate service installation on your system."
        exit 1
esac
exit 0