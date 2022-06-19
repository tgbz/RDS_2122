from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController

def topo():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)
    
    #4 switches with mac address 00:00:00:00:00:01, 00:00:00:00:00:02, 00:00:00:00:00:03, 00:00:00:00:00:04
    r1 = net.addSwitch('r1',dpid='0000000000000001')
    r2 = net.addSwitch('r2',dpid='0000000000000002')
    r3 = net.addSwitch('r3',dpid='0000000000000003')
    
    
    s1 = net.addSwitch('s1',dpid='0000000000000004')
    s2 = net.addSwitch('s2',dpid='0000000000000005')
    s3 = net.addSwitch('s3',dpid='0000000000000006')


    
    
    
    #Configuracao dos hosts
    #R&D Division (NETWORK A)
    h1 = net.addHost('h1', ip='10.0.1.2/24', mac='00:00:00:00:01:01', defaultRoute = 'via 10.0.1.1')
    h2 = net.addHost('h2', ip='10.0.1.3/24', mac='00:00:00:00:01:02', defaultRoute = 'via 10.0.1.1')
    h3 = net.addHost('h3', ip='10.0.1.4/24', mac='00:00:00:00:01:03', defaultRoute = 'via 10.0.1.1')
   
    #Client Support Division (NETWORK B)
    h4 = net.addHost('h4', ip='10.0.2.2/24', mac='00:00:00:00:01:04', defaultRoute = 'via 10.0.2.1')
    h5 = net.addHost('h5', ip='10.0.2.3/24', mac='00:00:00:00:01:05', defaultRoute = 'via 10.0.2.1')
    h6 = net.addHost('h6', ip='10.0.2.4/24', mac='00:00:00:00:01:06', defaultRoute = 'via 10.0.2.1')
    
    #Executive Division (NETWORK C)
    h7= net.addHost('h7', ip='10.0.3.2/24', mac='00:00:00:00:01:07', defaultRoute = 'via 10.0.3.1')
    h8 = net.addHost('h8', ip='10.0.3.3/24', mac='00:00:00:00:01:08', defaultRoute = 'via 10.0.3.1')
    h9 = net.addHost('h9', ip='10.0.3.4/24', mac='00:00:00:00:01:09', defaultRoute = 'via 10.0.3.1')
    
    
    #Execute webServer on web host
    #web.cmd('web python -m http.server 5555 &')
    
    #links intra-Routers
    net.addLink(r1, r2)
    net.addLink(r1, r3)
    net.addLink(r2, r3)
    
    #R&D Division - Network A
    net.addLink(r1, s1)
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s1, h3)
    
    #Client Support Division - Network B
    net.addLink(r2, s2)
    net.addLink(s2, h4)
    net.addLink(s2, h5)
    net.addLink(s2, h6)
    
    #Executive Division - Network C
    net.addLink(r3, s3)
    net.addLink(s3, h7)
    net.addLink(s3, h8)
    net.addLink(s3, h9)
        
        
    #addr intra-routers

    #Configuracao dos routers...
    r1.cmd('ifconfig r1-eth1 0')
    r1.cmd('ifconfig r1-eth2 0')
    r1.cmd('ifconfig r1-eth3 0')
    r1.cmd("ip addr add 10.0.1.1/24 brd + dev r1-eth1")#Link entre R1-S1
    r1.cmd("ip addr add 20.0.0.253/24 brd + dev r1-eth2") #Link entre R1-R2
    r1.cmd("ip addr add 30.0.0.253/24 brd + dev r1-eth3") #Link entre R1-R3
    r1.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward') 
    
    r2.cmd('ifconfig r1-eth1 0')
    r2.cmd('ifconfig r1-eth2 0')
    r2.cmd('ifconfig r1-eth3 0')
    r2.cmd("ip addr add 10.0.2.1/24 brd + dev r1-eth1")#Link entre R2-S2
    r2.cmd("ip addr add 20.0.0.254/24 brd + dev r1-eth2") #Link entre R1-R2
    r2.cmd("ip addr add 40.0.0.253/24 brd + dev r1-eth3") #Link entre R2-R3
    r2.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward') 


    r3.cmd('ifconfig r1-eth2 0')
    r3.cmd('ifconfig r1-eth3 0')
    r3.cmd('ifconfig r1-eth1 0')
    r3.cmd("ip addr add 10.0.1.3/24 brd + dev r1-eth1")#Link entre R3-S3
    r3.cmd("ip addr add 30.0.0.254/24 brd + dev r1-eth2") #Link entre R1-R3
    r3.cmd("ip addr add 40.0.0.254/24 brd + dev r1-eth3") #Link entre R2-R3
    r3.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward') 

    
    
    
    
    
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633, protocols='OpenFlow13')
    c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6634, protocols='OpenFlow13')
    
    
    net.build()
    
    #inicializacao
    c0.start()
    c1.start()
    r1.start([c0])
    r2.start([c0])
    r3.start([c0])
    s1.start([c1])
    s2.start([c1])
    s3.start([c1])
        
    CLI(net)
    net.stop()
    
if __name__ == "__main__":
    topo()
    setLogLevel('info')

    