## SYSTEMD CONFIG ##
Add new file sunshine.service with following script in path: /etc/systemd/
Then in console 'systemctl enable sunshine' and 'systemctl start sunshine'

[Unit]
Description=Dummy Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/repos/sunshine_rasp0/sunshine_rasp.py 
StandardInput=tty-force

[Install]
WantedBy=multi-user.target
