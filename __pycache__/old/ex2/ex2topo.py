from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch, RemoteController

def topo():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)
    
    #4 switches
    
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')
    
    #Configuracao dos hosts
    h1 = net.addHost('h1', ip='10.0.1.1/24', mac='00:00:00:00:00:01', defaultRoute = 'via 10.0.1.254')
    h2 = net.addHost('h2', ip='10.0.1.2/24', mac='00:00:00:00:00:02', defaultRoute = 'via 10.0.1.254')
    h3 = net.addHost('h3', ip='10.0.1.3/24', mac='00:00:00:00:00:03', defaultRoute = 'via 10.0.1.254')
    
    h4 = net.addHost('h4', ip='10.0.2.1/24', mac='00:00:00:00:00:04', defaultRoute = 'via 10.0.2.254')
    h5 = net.addHost('h5', ip='10.0.2.2/24', mac='00:00:00:00:00:05', defaultRoute = 'via 10.0.2.254')
    h6 = net.addHost('h6', ip='10.0.2.3/24', mac='00:00:00:00:00:06', defaultRoute = 'via 10.0.2.254')
    
    h7= net.addHost('h7', ip='10.0.3.1/24', mac='00:00:00:00:00:07', defaultRoute = 'via 10.0.3.254')
    h8 = net.addHost('h8', ip='10.0.3.2/24', mac='00:00:00:00:00:08', defaultRoute = 'via 10.0.3.254')
    h9 = net.addHost('h9', ip='10.0.3.3/24', mac='00:00:00:00:00:09', defaultRoute = 'via 10.0.3.254')
    
    #adicionar links
    net.addLink(s1, s2, delay='5ms')
    net.addLink(s1, s3, delay='5ms')
    net.addLink(s1, s4, delay='5ms')
    net.addLink(s2,h1)
    net.addLink(s2,h2)
    net.addLink(s2,h3)
    net.addLink(s3,h4,delay='5ms')
    net.addLink(s3,h5,delay='5ms')
    net.addLink(s3,h6,delay='5ms')
    net.addLink(s4,h7,loss=10)
    net.addLink(s4,h8,loss=10)
    net.addLink(s4,h9,loss=10)
               
    
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633, protocols='OpenFlow13')
    c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.2', port=6633, protocols='OpenFlow13')
    
    
    net.build()
    
    #inicializacao
    c0.start()
    s1.start([c0])
    s2.start([c1])
    s3.start([c1])
    s4.start([c1])
    
    CLI(net)
    net.stop()
    
if __name__ == "__main__":
    topo()
    setLogLevel('info')

    
    