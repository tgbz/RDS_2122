#!/bin/sh -x
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

xterm -maximized -hold -e "echo '########## Nanomsg Logs ##########'; sleep 9; sudo tools/nanomsg_client.py --thrift-port 9090" &
sleep 1;
xterm -hold -geometry 90x30+0+540 -e "echo '########## Compiling p4 ##########'; p4c-bm2-ss --p4v 16 p4/tp3-firewall.p4 -o json/tp3-firewall.json; echo '########## Opening Mininet Topology ##########'; sleep 3; sudo python3 mininet/tp3-topo.py --json json/tp3-firewall.json" &
process_id = $!
sleep 1;
xterm -hold -geometry 90x30+400+540 -e "echo '########## Injecting table entries ##########'; sleep 12; simple_switch_CLI --thrift-port 9090 < commands/commands.txt" &

wait $process_id