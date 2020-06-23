#!/bin/bash

mkdir -p /root/.mon/groups
cat > /root/.mon/groups/example <<EOF
{'example': ['127.0.0.1']}
EOF
./mon.py &
MON_PID=$!
./agg.py &
AGG_PID=$!
./scr.py

# clean up after the inevitable ^C
kill $MON_PID
kill $AGG_PID
