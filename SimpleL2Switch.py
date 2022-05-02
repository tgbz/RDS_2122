from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

class SimpleL2Switch(app_manager.RyuApp):
    """_summary_
        Para a implementação de uma app Ryu, e efectuada uma herança da ryu.bae.app_manager.RyuApp
        Utlizamos o OpenFlow v1.3
        Inicializamos o dicionário de mac addresses, correspondente à tabela
        
        No protocolo OpenFlow, alguns procedimentos tais como handshakres são necessários para a comunicação entre o switch OpenFlow e o controlador foram definidos.
    Args:
        app_manager (_type_): _description_
    """
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleL2Switch, self).__init__(*args, **kwargs)
        # initialize mac address table.
        self.mac_to_port = {}


    """
    Com o Ryu, quando uma mensagem OpenFlow é recebida, um evento correspondente à mensagem é gerado. A aplicação Ryu implementa um gestor de eventos correspondente à mensagem que deseja receber.
    
    Este gestor de eventos define uma função tendo um objecto evento para o argumento e usa o:
    
    ryu.controller.handler.set_ev_cls
    
    Esta classe (set_ev_cls) especifica a classe evento que suporta a mensagem recebida eo estado do switch OpenFlow para o argumento
    
    A classe evento é ryu.controller.ofp_event.EventOFP + <OpenFlow message name>.
    
    Por exemplo,
    
        No caso do de uma mensagem Packet-In, esta torna-se um EventOFPPacketIn.

        Exemplos:
        ryu.controller.handler.HANDSHAKE_DISPATCHER -> Troca de HELLOs
        
        ryu.controller.handler.CONFIG_DISPATCHER -> à espera de receber mensagens SwitchFeatures
        
        ryu.controller.handler.MAIN_DISPATCHER -> Estado normal.
        
        ryu.controller.handler.DEAD_DISPATCHER -> Desconexão de conexão
    
    Depois do handshake com o switch OpenFlow ser efetuado, uma flow-entry Table-miss é adicionada à flow table para ser tornada como pronta para receber uma mensagem Packet-In
    
    Em concreto, ao receber uma mensagem Switch Features (Features Reply), uma flow entry é adicionada 
    """
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
    
    """
    Na ev.msg, a instância da classe da mensagem OpenFlow correspondente ao evento é guardada. Neste caso, é ryu.ofproto.ofproto_v1_3_parser.OFPSwitchFeatures
    
    Na msg.datapath, a instância da classe ryu.controller.controller.Datapath correspondente ao switch OpenFlow que é emitio quando esta mensagem é guardada.
    
    A classe Datapath executa processamento importante tal como a efetiva comunicação com o switch OpenFlow e o evento corresponendete à mensagem recebida.
    
    Os atributos princiapsi utilizadas pelas aplicações Ryu são:
    
        id -> ID (data path ID) d switch OpenFlow conectado.
        
        ofproto -> indica o modulo ofproto que suporta a versão do OpenFlow em utilização. No caso do OpenFlow 1.3 irá ser o módulo:
                ryu.ofproto.ofproto_v1_3
                
        ofproto_parser -> o mesmo que ofproto, indica o modulo of_parser. No caso do OF 1.3:
                ryu.ofproto.ofproto_v1_3_parser
        
        os métodos principais da classe Datapath utilizada na aplicação Ryu são os seguintes:

            send_msg(msg) -> Envia a mensagem OpenFlow. Msg é uma sub classe do ryu.ofproto.ofproto_parser.MsgBase correspondente ao envio da mensagem
            
        O switching hub não utiliza propriamente a mensagem Switch Features em si.... É gerida como um evento para ober o timing e adicionar uma entrada de fluxo Table-Miss
    """
    
    
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

        
    """A flow entry Table-Miss tem a prioridade mínima (0) e a sua entrada corresponde a todos os pacotes. Na instrução desta antrada, através da especificação a acção de output para output na porta do contorlador, no caso do pacote recebido não corresponder a nenhuma das entradas de fluxo normais, um Packet-in é emitido.
    
    Uma correspondência fazia é gerada para correspondera todos os pacotes. Match é expresso na classe OFPMatch.
    
    De seguida, uma instância da classe OUTPUT action class (OFPActionOutput) é gerada para transferir para a porta de controlo. A porta de controlo é especificada como o output destination e OFPCML_NO_BUFFER é especificado para max_len de forma a enviar todos os pacotes para o controlador.
    
    Finalmente, 0 (lowest) é especiicado para prioridade e o método add_flow() é executado para enviar uma mensagem Flow Mod.
    """
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # get Datapath ID to identify OpenFlow switches.
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # analyse the received packets using the packet library.
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        # get the received port number from packet_in message.
        in_port = msg.match['in_port']

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        # if the destination mac address is already learned,
        # decide which port to output the packet, otherwise FLOOD.
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # construct action list.
        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time.
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        # construct packet_out message and send it.
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions,
                                  data=msg.data)
        datapath.send_msg(out)
        
    
    """
    Atributos OFPPacketIn:
        match -> instância da classe ryu.ofproto.ofproto_v1_3_parser.OFPMatch em que a meta informação dos pacotes recebidos é definida.
        
        data -> Data em formato binário indicando os pacotes recebidos em si
        
        total_len -> Comprimento da data dos pacotes recebidos.
        
        buffer_id -> Quando pacotes recebidos são buffered no OpenFlow Switch, indica o seu ID. Se não for buffered, ryu.ofproto.ofproto_v1_3.OFP_NO_BUFFER é definido. 
    """        
    
    