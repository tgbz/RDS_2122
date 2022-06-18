from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController

def topo():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)
    
    #4 switches with mac address 00:00:00:00:00:01, 00:00:00:00:00:02, 00:00:00:00:00:03, 00:00:00:00:00:04
    r1 = net.addSwitch('r1')
    r2 = net.addSwitch('r2')
    r3 = net.addSwitch('r3')
    
    r1.setMac('00:00:00:00:00:01','r1-eth1')
    r1.setMac('00:00:00:00:00:02','r1-eth2')
    r1.setMac('00:00:00:00:00:03','r1-eth3')      
    
    r2.setMac('00:00:00:00:00:04','r2-eth1')
    r2.setMac('00:00:00:00:00:05','r2-eth2')
    r2.setMac('00:00:00:00:00:06','r2-eth3')
    
    r3.setMac('00:00:00:00:00:07','r3-eth1')
    r3.setMac('00:00:00:00:00:08','r3-eth2')
    r3.setMac('00:00:00:00:00:09','r3-eth3')
    
    s1.setMac('00:00:00:00:02:01','s1-eth1')
    s1.setMac('00:00:00:00:02:02','s1-eth2')
    s1.setMac('00:00:00:00:02:03','s1-eth3')
    
    s2.setMac('00:00:00:00:02:04','s2-eth1')
    s2.setMac('00:00:00:00:02:05','s2-eth2')
    s2.setMac('00:00:00:00:02:06','s2-eth3')
    
    s3.setMac('00:00:00:00:02:07','s3-eth1')
    s3.setMac('00:00:00:00:02:08','s3-eth2')
    s3.setMac('00:00:00:00:02:09','s3-eth3')
    

    
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')


    
    
    
    #Configuracao dos hosts
    #R&D Division
    web = net.addHost('web', ip='10.0.1.2/24', mac='00:00:00:00:01:01', defaultRoute = 'via 10.0.1.1')
    h1 = net.addHost('h1', ip='10.0.1.3/24', mac='00:00:00:00:01:02', defaultRoute = 'via 10.0.1.1')
    h2 = net.addHost('h2', ip='10.0.1.4/24', mac='00:00:00:00:01:03', defaultRoute = 'via 10.0.1.1')
   
    #Client Support Division
    h3 = net.addHost('h3', ip='10.0.2.2/24', mac='00:00:00:00:01:04', defaultRoute = 'via 10.0.2.1')
    h4 = net.addHost('h4', ip='10.0.2.3/24', mac='00:00:00:00:01:05', defaultRoute = 'via 10.0.2.1')
    h5 = net.addHost('h5', ip='10.0.2.4/24', mac='00:00:00:00:01:06', defaultRoute = 'via 10.0.2.1')
    
    #Executive Division
    h6= net.addHost('h7', ip='10.0.3.2/24', mac='00:00:00:00:01:07', defaultRoute = 'via 10.0.3.1')
    h7 = net.addHost('h8', ip='10.0.3.3/24', mac='00:00:00:00:01:08', defaultRoute = 'via 10.0.3.1')
    h8 = net.addHost('h9', ip='10.0.3.4/24', mac='00:00:00:00:01:09', defaultRoute = 'via 10.0.3.1')
    
    
    #Execute webServer on web host
    web.cmd('web python -m http.server 5555 &')
    
    #links intra-Routers
    net.addLink(r1, r2)
    net.addLink(r1, r3)
    net.addLink(r2, r3)
    
    #R&D Division - Network A
    net.addLink(r1, s1)
    net.addLink(s1, web)
    net.addLink(s1,h1)
    net.addLink(s1,h2)
    
    #Client Support Division - Network B
    net.addLink(r2, s2)
    net.addLink(s2, h3)
    net.addLink(s2, h4)
    net.addLink(s2, h5)
    
    #Executive Division - Network C
    net.addLink(r3, s3)
    net.addLink(s3, h6)
    net.addLink(s3, h7)
    net.addLink(s3, h8)
    
    
    

    
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

    