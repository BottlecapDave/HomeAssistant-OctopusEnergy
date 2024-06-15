#!/bin/bash
set -e

rm -r bottlecapdave_homeassistant_octopus_energy
mkdir bottlecapdave_homeassistant_octopus_energy
cd bottlecapdave_homeassistant_octopus_energy
wget https://raw.githubusercontent.com/BottlecapDave/HomeAssistant-OctopusEnergy/develop/home_pro_server/oeha_server.py
chmod +x oeha_server.py
wget https://raw.githubusercontent.com/BottlecapDave/HomeAssistant-OctopusEnergy/develop/home_pro_server/start_server.sh
chmod +x start_server.sh