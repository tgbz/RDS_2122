"""
Topologia com 1 switch e 4 hosts

         SDN CONTROLLER
                |
                |
                |
              switch
    |       |       |       |
   h1      h2       h3      h4
                
Ao adicionar o dicionário 'topos' com um valor chave/valor para gerar a nossa nova topologia permite
a passagem de parâmetros para o '--topo=mytopo' pela linha de comandos
"""

from mininet.topo import Topo

class MyTopo(Topo):
    
    def build(self):
        # Add hosts and switches
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        
        s1 = self.addSwitch('s1')
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)
        
topos = {'mytopo': (lambda: MyTopo())}