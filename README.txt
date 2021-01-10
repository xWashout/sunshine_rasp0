## SYSTEMD CONFIG ##
Add new file sunshine.service with following script in path: /etc/systemd/

[Unit]
Description=Sunshine Runner

Wants=network.target
After=syslog.target network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/sunshine_runner.sh
Restart=on-failure
RestartSec=10
KillMode=process

[Install]
WantedBy=multi-user.target

## Add new script sunshine_runner.sh in path: /usr/local/bin ##

#!/bin/bash

echo "Starting Sunshine Runner"

python3 /home/pi/repos/sunshine_rasp0/sunshine_rasp.py
 

