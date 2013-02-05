'''
Created on Jan 27, 2011

@author: capveg
'''

import logging

import basic
import testutils
from oftest import cstruct as ofp

ETHERTYPE_VLAN = 0x8100

def test_set_init(config):
    """
    Set up function for cross_connection test classes

    @param config The configuration dictionary; see oft
    """

    global cross_connection_port_map
    global cross_connection_logger
    global cross_connection_config

    cross_connection_logger = logging.getLogger("cross_connection")
    cross_connection_logger.info("Initializing test set")
    cross_connection_port_map = config["port_map"]
    cross_connection_config = config

name_to_port_map = {
    'D1-ADD' : 1,
    'D2-ADD' : 2,
    'D3-ADD' : 3,
    'D4-ADD' : 4,
    'D1-DROP': 257,
    'D2-DROP': 258,
    'D3-DROP': 259,
    'D4-DROP': 260,
    'D1-IN'  : 513,
    'D2-IN'  : 514,
    'D3-IN'  : 515,
    'D4-IN'  : 516,
    'D1-OUT' : 769,
    'D2-OUT' : 770,
    'D3-OUT' : 771,
    'D4-OUT' : 772
}

class FlowModAdd(basic.SimpleProtocol):
    """ Simple FlowMod Modify test
    delete all flows in the table
    insert an exact match flow_mod sending to port[1]
    then swap the output action from port[1] to port[2]
    then get flow_stats
    assert that the new actions are in place
    """
    def runTest(self):
        # ing_port = cross_connection_port_map.keys()[0]
        # out_port1 = cross_connection_port_map.keys()[1]
        # out_port2 = cross_connection_port_map.keys()[2]
        ing_port = name_to_port_map['D1-ADD']
        out_port = name_to_port_map['D4-OUT']
        print "ing_port  = "  + str(ing_port)
        print "out_port  = "  + str(out_port)
        pkt = testutils.simple_tcp_packet()
        match_fm = ofp.ofp_match()
        match_fm.in_port = ing_port
        match_fm.dl_type = ETHERTYPE_VLAN
        match_fm.dl_vlan = 1
        fm_orig = testutils.flow_msg_create(self, pkt, match=match_fm,
                                            ing_port=ing_port, 
                                            egr_port=out_port)
        # fm_new = testutils.flow_msg_create(self, match_fm,
        #                                     ing_port=ing_port, 
        #                                     egr_port=out_port2)
        # fm_new.command = ofp.OFPFC_MODIFY_STRICT
        rv = self.controller.message_send(fm_orig)
        self.assertEqual(rv, 0, "Failed to insert 1st flow_mod")
        testutils.do_barrier(self.controller)
        # rv = self.controller.message_send(fm_new)
        # testutils.do_barrier(self.controller)
        # self.assertEqual(rv, 0, "Failed to insert 2nd flow_mod")
        # flow_stats = testutils.flow_stats_get(self)
        # self.assertEqual(len(flow_stats.stats),1, 
        #                  "Expected only one flow_mod")
        # stat = flow_stats.stats[0]
        # self.assertEqual(stat.match, fm_new.match)
        # self.assertEqual(stat.instructions, fm_new.instructions)
        # @todo consider adding more tests here
        
class FlowStatsGet(basic.SimpleProtocol):
    """
    Get stats 

    Simply verify stats get transaction
    """
    def runTest(self):
        cross_connection_logger.info("Running StatsGet")
        cross_connection_logger.info("Inserting trial flow")
        ing_port = name_to_port_map['D2-ADD']
        out_port = name_to_port_map['D3-DROP']
        print "ing_port  = "  + str(ing_port)
        print "out_port  = "  + str(out_port)
        pkt = testutils.simple_tcp_packet()
        match_fm = ofp.ofp_match()
        match_fm.in_port = ing_port
        match_fm.dl_type = ETHERTYPE_VLAN
        match_fm.dl_vlan = 1
        request = testutils.flow_msg_create(self, pkt, match=match_fm,
                                            ing_port=ing_port, 
                                            egr_port=out_port)

        rv = self.controller.message_send(request)
        self.assertTrue(rv != -1, "Failed to insert test flow")
        
        cross_connection_logger.info("Sending flow request")
        response = testutils.flow_stats_get(self)
        cross_connection_logger.debug(response.show())


if __name__ == "__main__":
    print "Please run through oft script:  ./oft --test_spec=cross_connection"