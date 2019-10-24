#!/bin/bash
cd ~/src-v2/SARndbox-2.5/
server-env/bin/python -m sandbox.server.main &
sleep 5
./bin/SARndbox -uhm -fpv -evr -0.005 -slf ./BoxLayout.txt
