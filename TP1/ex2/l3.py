from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu import utils


class l3(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(l3, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
    ''' 
    - Gestor de eventos respnosável por novos switches, este gestor de eventos especifica as acções a serem tomadas para um evento em particular tal como um pacote a entrar. O decorador set_ev_cls menciona que a classe do evento por trás da mensagem a entrar e o status do OpenFlow switch
    '''   
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        #Instalação da table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("switch:%s conected", dpid)
    '''
    - Função para adicionar flow entries, adicionando uma match condition, um conjunto de acções assim como o tempo efectivo e prioridade de entrada para o pacote em cada nova flow entry
        - Funcionalidaes adicionais adicionadas ao switch para continuar o processamento de fluxo numa diferente tabela ou mesmo a escrita de metadata para o switch... são escritas com um simples set de instruções
            - datapath: representa o switch que diparou o evento, referenciado por uma variavel local datapath
            - priority: prioridade de entrada para o flow entry representado por um inteiro
            - actions: Lista de acções que vão ser enviadas dentro do flow mod
            - buffer_id: Parametro opcional que indica se um pacote é buffered para o switch e depois enviado para o controller.
    '''
    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,priority=priority, match=match,instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        
        datapath.send_msg(mod)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("pacote truncado: apenas %s de %s bytes", ev.msg.total_len, ev.msg_len)

        #data
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        #analise da data
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        if eth.ethertype == ether.ETH_TYPE_LLDP:
            return
        
        #Criacao da tabela mac-port que contém o endereço source do pacote associado com a porta a que chegou.
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        
        #Encontrar o destino.
        
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        
        actions = [parser.OFPActionOutput(out_port)]
        
        #enviar flow entry
        if out_port!=ofproto.OFPP_FLOOD:
            if l3.ethertype == ether.ETH_TYPE_IP:
                ip=pkt.get_protocols(ipv4.ipv4)
                srcip=ip.src
                dstip=ip.dst
                match=parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,ipv4_src=srcip,ipv4_dst=dstip)
        
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath,1,match,actions,msg.buffer_id)
            
            else:
                self.add_flow(datapath,1,match,actions)
            
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
        
        