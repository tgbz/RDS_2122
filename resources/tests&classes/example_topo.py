
from asyncio import protocols
from mininet.net import Mininet, VERSION
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController


def topo():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    h1 = net.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute = 'via 10.0.1.254')
    h2 = net.addHost('h2', ip='10.0.2.1/24', mac='00:00:00:00:00:02', defaultRoute = 'via 10.0.2.254')
    h3 = net.addHost('h3', ip='10.0.3.1/24', mac='00:00:00:00:00:03', defaultRoute = 'via 10.0.3.254')

    r0 = net.addSwitch('r0', dpid='0000000000000001', protocols='OpenFlow13')

   

    net.addLink(h1, r0)#, intfName2='r0-eth0', params2={ 'ip' : '10.0.1.254/24' })
    net.addLink(h2, r0)#, intfName2='r0-eth1', params2={ 'ip' : '10.0.2.254/24' })
    net.addLink(h3, r0)#, intfName2='r0-eth2', params2={ 'ip' : '10.0.3.254/24' })

    """
    list = r0.intfList()

    mac = 11

    for i in range(1, len(list)):
        list[i].setMAC("00:00:00:00:00:%s" %mac)
        mac += 1
    """
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633, protocols='OpenFlow13')
    



    net.build()
    #net.start()
    c0.start()
    r0.start([c0])

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    topo()