#!/bin/bash

set -x
set -e

export LC_ALL=C

pio log -m "Restarting MQTT to DB streaming" -l info
sudo systemctl restart pioreactor_startup_run@mqtt_to_db_streaming.service
