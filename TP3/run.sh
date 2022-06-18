#!/bin/sh -x
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

xterm -maximized -hold -e "echo 'Opening 3 terminals... Move this terminal'; echo '########## Nanomsg Logs ##########'; sleep 9; sudo tools/nanomsg_client.py --thrift-port 9090" &
sleep 1;
xterm -hold -e "echo 'Opening 3 terminals... Move this terminal'; echo '########## Compiling p4 & Opening Mininet Topology ##########'; p4c-bm2-ss --p4v 16 p4/tp3-firewall.p4 -o json/tp3-firewall.json; sleep 3; sudo python3 mininet/tp3-topo.py --json json/tp3-firewall.json" &
process_id = $!
sleep 1;
xterm -hold -e "echo 'Opening 3 terminals... Move this terminal'; echo '########## Injecting table entries ##########'; sleep 12; simple_switch_CLI --thrift-port 9090 < commands/commands.txt" &

wait $process_id