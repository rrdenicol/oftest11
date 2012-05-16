import logging
import sys
import struct

import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.instruction as instruction
import groups as groups
import oftest.bucket as bucket
import basic
import pktact
#import oftest.controller as controller

import testutils

#Import scappy packet generator
try:
    import scapy.all as scapy
except:
    try:
        import scapy as scapy
    except:
        sys.exit("Need to install scapy for packet parsing")

#@var rtp_port_map Local copy of the configuration map from OF port
# numbers to OS interfaces
rtp_port_map = None
#@var rtp_logger Local logger object
rtp_logger = None
#@var rtp_config Local copy of global configuration data
rtp_config = None


def test_set_init(config):
    """
    Set up function for IPv6 packet handling test classes

    @param config The configuration dictionary; see oft
    """

    global rtp_port_map
    global rtp_logger
    global rtp_config

    rtp_logger = logging.getLogger("rtp")
    rtp_logger.info("Initializing test set")
    rtp_port_map = config["port_map"]
    rtp_config = config


class NewTest(basic.SimpleDataPlane):
    """
    Insert a flow

    Three groups with several action buckets
    """
    def send_ctrl_exp_noerror(self, msg, log = ''):
        rtp_logger.info('Sending message ' + log)
        rtp_logger.debug(msg.show())
        rv = self.controller.message_send(msg)
        self.assertTrue(rv != -1, 'Error sending!')

        rtp_logger.info('Waiting for error messages...')
        (response, raw) = self.controller.poll(ofp.OFPT_ERROR, 1)

        self.assertTrue(response is None, 'Unexpected error message received')

        testutils.do_barrier(self.controller);
    def runTest(self):
    
        of_ports = rtp_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port = of_ports[3]
        
        rtp_logger.info("Running " + str(self))
        
        rtp_logger.info("Removing all flows")
        testutils.delete_all_flows(self.controller, rtp_logger)
        testutils.delete_all_groups(self.controller, rtp_logger)
        
        group_add_msg = \
        groups.create_group_mod_msg(ofp.OFPGC_ADD, ofp.OFPGT_ALL, group_id = 10, buckets = [
            groups.create_bucket(0, 0, 0, [
                groups.create_action(action= ofp.OFPAT_OUTPUT, port= of_ports[1])
            ]) ,
            groups.create_bucket(0, 0, 0, [
                groups.create_action(action= ofp.OFPAT_SET_DL_DST, dl_dst='00:00:00:00:00:02'),
                groups.create_action(action= ofp.OFPAT_SET_NW_DST, nw_dst='192.168.3.1'),
                groups.create_action(action= ofp.OFPAT_OUTPUT, port= of_ports[2])
            ]) 
        ])

        self.send_ctrl_exp_noerror(group_add_msg, 'group add')
        
        group_add_msg = \
        groups.create_group_mod_msg(ofp.OFPGC_ADD, ofp.OFPGT_ALL, group_id = 20, buckets = [
            groups.create_bucket(0, 0, 0, [
                groups.create_action(action= ofp.OFPAT_OUTPUT, port= of_ports[1])
            ]) 
        ])

        self.send_ctrl_exp_noerror(group_add_msg, 'group add')
        
        group_add_msg = \
        groups.create_group_mod_msg(ofp.OFPGC_ADD, ofp.OFPGT_SELECT, group_id = 30, buckets = [
            groups.create_bucket(1, 0, 0, [
                groups.create_action(action= ofp.OFPAT_GROUP, group_id = 10)
            ]) ,
            groups.create_bucket(1, 0, 0, [
                groups.create_action(action= ofp.OFPAT_GROUP, group_id = 20)
            ])
        ])

        self.send_ctrl_exp_noerror(group_add_msg, 'group add')
        
        request = message.flow_mod()

        pkt = testutils.simple_rtp_packet()
        # Gerar o flow_mod em cima do pacote RTP (desconsidera a sequencia do RTP)
        flow_add_msg = \
        groups.create_flow_msg(packet = pkt, in_port = of_ports[0], apply_action_list = [
            groups.create_action(action = ofp.OFPAT_GROUP, group_id = 30),
        ])
        
        rv = self.controller.message_send(flow_add_msg)
        self.assertTrue(rv != -1, "Error installing flow mod")
        
        idx = 0
        
        while idx < 100 :
            ingress_port = of_ports[0]
            
            pkt = testutils.simple_rtp_packet(rtp_sequence= idx)
            
            rtp_logger.info("Sending packet to dp port " + 
                               str(ingress_port))
            self.dataplane.send(ingress_port, str(pkt))
            if idx%2 == :
            
            idx = idx + 1
#            yes_ports = set([egress_port1, egress_port2])
#            no_ports = set(of_ports).difference(yes_ports)

#            testutils.receive_pkt_check(self.dataplane, pkt, yes_ports, no_ports, self, rtp_logger)

        testutils.delete_all_flows(self.controller, rtp_logger)
        testutils.delete_all_groups(self.controller, rtp_logger)
        
        
        
        
if __name__ == "__main__":
    print "Please run through oft script:  ./oft --test-spec=newtest"
