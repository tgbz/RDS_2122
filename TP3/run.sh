#!/bin/sh -x
xterm -hold -e "echo 'Opening 3 terminals'; sleep 5; simple_switch_CLI --thrift-port 9090 < commands/commands.txt > commands/commands_log.txt" &
xterm -hold -e "sleep 7; sudo tools/nanomsg_client.py --thrift-port 9090" &
xterm -hold -e "p4c-bm2-ss --p4v 16 p4/tp3-firewall.p4 -o json/tp3-firewall.json; sleep 2; sudo python3 mininet/tp3-topo.py --json json/tp3-firewall.json" &