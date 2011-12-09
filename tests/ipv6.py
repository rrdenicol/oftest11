"""
Test cases for testing actions taken on packets

See basic.py for other info.

It is recommended that these definitions be kept in their own
namespace as different groups of tests will likely define 
similar identifiers.

  The function test_set_init is called with a complete configuration
dictionary prior to the invocation of any tests from this file.

  The switch is actively attempting to contact the controller at the address
indicated oin oft_config

"""



import logging


import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.instruction as instruction
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


import os.path
import subprocess

#@var port_map Local copy of the configuration map from OF port
# numbers to OS interfaces
pa_port_map = None
#@var pa_logger Local logger object
pa_logger = None
#@var pa_config Local copy of global configuration data
pa_config = None

# For test priority
#@var test_prio Set test priority for local tests
test_prio = {}

WILDCARD_VALUES = [ofp.OFPFW_IN_PORT,
                   ofp.OFPFW_DL_VLAN,
                   ofp.OFPFW_DL_TYPE,
                   ofp.OFPFW_NW_PROTO,
                   ofp.OFPFW_DL_VLAN_PCP,
                   ofp.OFPFW_NW_TOS]

MODIFY_ACTION_VALUES =  [ofp.OFPAT_SET_VLAN_VID,
                         ofp.OFPAT_SET_VLAN_PCP,
                         ofp.OFPAT_SET_DL_SRC,
                         ofp.OFPAT_SET_DL_DST,
                         ofp.OFPAT_SET_NW_SRC,
                         ofp.OFPAT_SET_NW_DST,
                         ofp.OFPAT_SET_NW_TOS,
                         ofp.OFPAT_SET_TP_SRC,
                         ofp.OFPAT_SET_TP_DST]

# Cache supported features to avoid transaction overhead
cached_supported_actions = None

TEST_VID_DEFAULT = 2

def test_set_init(config):
    """
    Set up function for IPv6 packet handling test classes

    @param config The configuration dictionary; see oft
    """

    global pa_port_map
    global pa_logger
    global pa_config

    pa_logger = logging.getLogger("ipv6")
    pa_logger.info("Initializing test set")
    pa_port_map = config["port_map"]
    pa_config = config

# chesteve: IPv6 packet gen
def simple_ipv6_packet(pktlen=1000, 
                      dl_dst='00:01:02:03:04:05',
                      dl_src='00:06:07:08:09:0a',
                      dl_vlan_enable=False,
                      dl_vlan=0,
                      dl_vlan_pcp=0,
                      dl_vlan_cfi=0,
                      ip_src='fe80::2420:52ff:fe8f:5189',
                      ip_dst='fe80::2420:52ff:fe8f:5190',
                      ip_tos=0,
                      tcp_sport=0,
                      tcp_dport=0, 
                      EH = False, 
                      EHpkt = scapy.IPv6ExtHdrDestOpt()
                      ):

    """
    Return a simple dataplane IPv6 packet 

    Supports a few parameters:
    @param len Length of packet in bytes w/o CRC
    @param dl_dst Destinatino MAC
    @param dl_src Source MAC
    @param dl_vlan_enable True if the packet is with vlan, False otherwise
    @param dl_vlan VLAN ID
    @param dl_vlan_pcp VLAN priority
    @param ip_src IPv6 source
    @param ip_dst IPv6 destination
    @param ip_tos IP ToS
    @param tcp_dport TCP destination port
    @param ip_sport TCP source port

    Generates a simple TCP request.  Users
    shouldn't assume anything about this packet other than that
    it is a valid ethernet/IP/TCP frame.
    """
    # Note Dot1Q.id is really CFI
    if (dl_vlan_enable):
        pkt = scapy.Ether(dst=dl_dst, src=dl_src)/ \
            scapy.Dot1Q(prio=dl_vlan_pcp, id=dl_vlan_cfi, vlan=dl_vlan)/ \
            scapy.IP(src=ip_src, dst=ip_dst, tos=ip_tos)

    else:
        pkt = scapy.Ether(dst=dl_dst, src=dl_src)/ \
            scapy.IPv6(src=ip_src, dst=ip_dst)

    # Add IPv6 Extension Headers 
    if EH:
        pkt = pkt / EHpkt

    if (tcp_sport >0 and tcp_dport >0):
        pkt = pkt / scapy.TCP(sport=tcp_sport, dport=tcp_dport)

    pktlen = len(pkt) # why??
    pkt = pkt/("D" * (pktlen - len(pkt)))

    return pkt

def nxm_send_flow_mod_add(flow_match,flow_acts,logger):
    """
    Send a flow mod with the nxm operation mode
    """

    of_dir = os.path.normpath("../../of11softswitchv6")
    ofd = os.path.normpath(of_dir + "/udatapath/ofdatapath")
    dpctl = os.path.normpath(of_dir + "/utilities/dpctl")
    dpctl_switch = "unix:/tmp/ofd"

    flow_cmd1 = "flow-mod"
    flow_cmd2 = "-F"
    flow_cmd3 = "nxm" 
    flow_cmd4 = "cmd=add,table=0,idle=100"

    pcall = [dpctl, dpctl_switch, flow_cmd1, flow_cmd2, flow_cmd3, flow_cmd4, flow_match,  flow_acts]
    #print pcall
    rv = subprocess.call(pcall)

    return rv

def nxm_delete_all_flows():
    of_dir = os.path.normpath("../../of11softswitchv6")
    ofd = os.path.normpath(of_dir + "/udatapath/ofdatapath")
    dpctl = os.path.normpath(of_dir + "/utilities/dpctl")
    dpctl_switch = "unix:/tmp/ofd"

    flow_cmd1 = "flow-mod"
    flow_cmd2 = "-F"
    flow_cmd3 = "nxm" 
    flow_cmd4 = "cmd=del,table=0"
    flow_cmd5 = "wildcards=all"
    pcall = [dpctl, dpctl_switch, flow_cmd1, flow_cmd2, flow_cmd3, flow_cmd4, flow_cmd5]
    rv = subprocess.call(pcall) 

    return rv

def request_flow_stats():

    of_dir = os.path.normpath("../../of11softswitchv6")
    ofd = os.path.normpath(of_dir + "/udatapath/ofdatapath")
    dpctl = os.path.normpath(of_dir + "/utilities/dpctl")
    dpctl_switch = "unix:/tmp/ofd"

    pa_logger.debug("Request stats-flow")  
    pcall = [dpctl, dpctl_switch,"-F","nxm", "stats-flow"]  #  
    #subprocess.call(pcall)


# TESTS
class MatchIPv4Simple(basic.SimpleDataPlane):
    """
    Just send a packet IPv4 / TCP thru the switch
    """
    def runTest(self):
        
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port = of_ports[3]
        
        # Remove all entries Add entry match all
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry match all
        flow_match = "wildcards=none,dl_src_mask=ff:ff:ff:ff:ff:ff,dl_dst_mask=ff:ff:ff:ff:ff:ff,nw_src_mask=255.255.255.255,nw_dst_mask=255.255.255.255,meta_mask=0xffffffffffffffff" #, -in_port,in_port=1,dl_type=2048in_port=0  wildcards=0xffff
        flow_acts = "apply:output=" + str(egr_port)
        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

        #Send packet
        pkt = testutils.simple_tcp_packet()
        pa_logger.info("Sending IPv4 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))
        
        #Receive packet
        exp_pkt = testutils.simple_tcp_packet()
        testutils.receive_pkt_verify(self, egr_port, exp_pkt)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        #rc = testutils.delete_all_flows(self.controller, pa_logger)
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")

#        pa_logger.debug("Request stats-table")  
#        pcall = [self.dpctl, dpctl_switch, "stats-table"]  #  stats-flow
#        subprocess.call(pcall)

class MatchIPv6Simple(basic.SimpleDataPlane):
    """
    Just send a packet IPv6 to match a simple entry on the matching table
    """
    def runTest(self):
        
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port = of_ports[3]
        
        # Remove all entries Add entry match all
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry match 
        flow_match = "wildcards=none,nw_src_ipv6=fe80::2420:52ff:fe8f:5189,nw_dst_ipv6=fe80::2420:52ff:fe8f:5190"
        flow_acts = "apply:output=" + str(egr_port)
        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

        #Send packet
        pkt = simple_ipv6_packet(EH = True)
        pa_logger.info("Sending IPv6 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))
        
        #Receive packet
        exp_pkt = simple_ipv6_packet(EH = True)
        testutils.receive_pkt_verify(self, egr_port, exp_pkt)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        #rc = testutils.delete_all_flows(self.controller, pa_logger)
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")


class AllWildcardMatchIPv4(basic.SimpleDataPlane):
    """
    Just match an IPv4 packet thru the switch
    """
    def runTest(self):
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")

        pkt = testutils.simple_tcp_packet()
        testutils.flow_match_test(self, pa_port_map, pkt=pkt,  wildcards=ofp.OFPFW_ALL, max_test =1)

        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")


class SanityCheck(basic.SimpleDataPlane):
    """
    Check if a flow mod with non-consistent fields is installed or not
    """
    def runTest(self):

        # Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port = of_ports[3]
        
        # Remove flows
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry with invalid arguments (wrong dl_type for a IPv4 packet)
        flow_match = "wildcards=none,dl_type=0x7000,nw_src=192.168.0.1"
        flow_acts = "apply:output=" + str(egr_port)
        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")
       
	
        #Send IPv4 packet 

        pkt = testutils.simple_tcp_packet()

        pa_logger.info("Sending IPv4 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))

        pkt = testutils.simple_tcp_packet()
        pa_logger.info("Sending IPv4 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))
        
        #Should not receive packet
        exp_pkt = testutils.simple_tcp_packet()
	testutils.receive_pkt_check(self.dataplane, exp_pkt, [], of_ports, self,
                              pa_logger)

        #See flow match
        request_flow_stats()

#        rc = testutils.delete_all_flows(self.controller, pa_logger)
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")



class MatchIPv6HBH(basic.SimpleDataPlane):
    """
    Just send an IPv6 packet with Hop-by-Hop Extension Header thru the switch
    """
    def runTest(self):
               
	# Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port =   of_ports[3]
        
        
        # Remove flows
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry match ipv6 packets with hop-by-hop  
        flow_match = "wildcards=none,in_port=1,hbh_ipv6"
        flow_acts = "apply:output=" + str(egr_port)

        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

        #Send packet
	pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()) 

 	print "Sending IPv6 packet to " + str(ing_port)
        pa_logger.info("Sending IPv6 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        
	self.dataplane.send(ing_port, str(pkt))


        #Receive packet
        exp_pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()) 

        testutils.receive_pkt_verify(self, egr_port, exp_pkt)

        #See flow match
        request_flow_stats()
        
        #Remove flows
#        rc = testutils.delete_all_flows(self.controller, pa_logger)
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")

class MatchIPv6RH(basic.SimpleDataPlane):
    """
    Just send an IPv6 packet with the Routing Extension Header thru the switch
    """
    def runTest(self):
               
	# Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port =   of_ports[3]
        
        # Remove flows
        rc = nxm_delete_all_flows()
#        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry match all 
	#sudo dpctl unix:/tmp/ofd -F nxm flow-mod cmd=add,table=0,idle=100 wildcards=none,in_port=1,hbh_ipv6 apply:output=4

        flow_match = "wildcards=none,in_port=1,rh_ipv6"
        flow_acts = "apply:output=" + str(egr_port)

        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

        #Send packet
	pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrRouting()) 

 	print "Sending IPv6 packet to " + str(ing_port)
        pa_logger.info("Sending IPv6 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        
	self.dataplane.send(ing_port, str(pkt))


        #Receive packet
        exp_pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrRouting()) 

        testutils.receive_pkt_verify(self, egr_port, exp_pkt)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        rc = nxm_delete_all_flows()
#        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

class MatchIPv6HBHandRH(basic.SimpleDataPlane):

    def runTest(self):

        # Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port =   of_ports[3]
        
        # Remove flows
        rc = nxm_delete_all_flows()
#        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry match all 
	#sudo dpctl unix:/tmp/ofd -F nxm flow-mod cmd=add,table=0,idle=100 wildcards=none,in_port=1,hbh_ipv6 apply:output=4

        flow_match = "wildcards=none,hbh_ipv6,rh_ipv6"
        flow_acts = "apply:output=" + str(egr_port)

        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

	#Send IPv6 packet with Routing Header

        pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrRouting())

        pa_logger.info("Sending IPv6 RH packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))
        
        #Receive packet
        #exp_pkt = testutils.simple_tcp_packet()
	testutils.receive_pkt_check(self.dataplane, pkt, [], of_ports, self,
                              pa_logger)

        #See flow match
        request_flow_stats()
	
	#Send IPv6 packet with both Headers
        #pkt = simple_ipv6_packet()        
	pktv6 = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()/scapy.IPv6ExtHdrRouting()) 
        print "Sending IPv6 HBH+RH packet to " + str(ing_port)
        pa_logger.info("Sending IPv6 HBH+RH packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        
	self.dataplane.send(ing_port, str(pktv6))


        #Receive packet
        #exp_pkt = simple_ipv6_packet()
        exp_pktv6 = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()/scapy.IPv6ExtHdrRouting()) 

        testutils.receive_pkt_verify(self, egr_port, exp_pktv6)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        rc = nxm_delete_all_flows()
#        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")


class MatchIPv6TCP(basic.SimpleDataPlane):

    def runTest(self):
        	# Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port =   of_ports[3]
        
        # Remove flows
        rc = nxm_delete_all_flows()
        #rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

        # Add entry match all 
        flow_match = "wildcards=none,in_port=1,tp_src=80,tp_dst=8080"
        flow_acts = "apply:output=" + str(egr_port)

        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

        #Send packet
        pkt = simple_ipv6_packet(tcp_sport=80, tcp_dport=8080) 

        print "Sending IPv6 packet to " + str(ing_port)
        pa_logger.info("Sending IPv6 packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        
        self.dataplane.send(ing_port, str(pkt))

        #Receive packet
        #exp_pkt = simple_ipv6_packet()
        exp_pkt = simple_ipv6_packet(tcp_sport=80, tcp_dport=8080) 

        testutils.receive_pkt_verify(self, egr_port, exp_pkt)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        #rc = testutils.delete_all_flows(self.controller, pa_logger)
        rc = nxm_delete_all_flows()        
        self.assertEqual(rc, 0, "Failed to delete all flows")


class MatchIPv6RoutingAddress(basic.SimpleDataPlane):

    def runTest(self):

        # Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port =   of_ports[3]
        
        # Remove flows
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

	# Add Entry wich matches packets with hbh_code = 0

        flow_match = "wildcards=none,dl_type=0x86DD,rh_ipv6,rh_add_ipv6=ff01::0001"
        flow_acts = "apply:output=" + str(egr_port)

        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

	#Send IPv6 packet with Routing Header

        pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrRouting(addresses=['ff01::0001','ff02::0000']))

        pa_logger.info("Sending IPv6 RH packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))
        
        #See flow match
        request_flow_stats()
	
	#Receive packet
        exp_pktv6 = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrRouting(addresses=['ff01::0001','ff02::0000'])) 

        testutils.receive_pkt_verify(self, egr_port, exp_pktv6)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        #rc = testutils.delete_all_flows(self.controller, pa_logger)
        rc = nxm_delete_all_flows()
        self.assertEqual(rc, 0, "Failed to delete all flows")

"""
class MatchIPv6HBHOptCode(basic.SimpleDataPlane):

    def runTest(self):

        # Config
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        egr_port =   of_ports[3]
        
        # Remove flows
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

	# Add Entry wich matches packets with hbh_code = 0

        flow_match = "wildcards=none,hbh_ipv6,hbh_code_ipv6=0"
        flow_acts = "apply:output=" + str(egr_port)

        rc = nxm_send_flow_mod_add(flow_match,flow_acts,pa_logger)
        self.assertEqual(rc, 0, "Failed to add flow entry")

	#Send IPv6 packet with Routing Header

        pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()/scapy.IPv6)

        pa_logger.info("Sending IPv6 RH packet to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))
        
        #See flow match
        request_flow_stats()
	
	#Receive packet
        exp_pktv6 = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()/scapy.IPv6ExtHdrRouting()) 

        testutils.receive_pkt_verify(self, egr_port, exp_pktv6)

        #See flow match
        request_flow_stats()
        
        #Remove flows
        rc = testutils.delete_all_flows(self.controller, pa_logger)
        self.assertEqual(rc, 0, "Failed to delete all flows")

"""

class PacketOnlyIPv6TCP(basic.DataPlaneOnly):
    """
    Just send an IPv6 packet with TCP ports thru the switch
    """
    def runTest(self):
        
        pkt = simple_ipv6_packet( tcp_sport=80, tcp_dport=8080)
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        pa_logger.info("Sending IPv6 packet with TCP to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))

class PacketOnlyIPv6HBH(basic.DataPlaneOnly):
    """
    Just send an IPv6 packet with Hop-by-Hop EH thru the switch
    """
    def runTest(self):
        
        pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()) 
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        pa_logger.info("Sending IPv6 packet with Hop-by-Hop EH to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))


class PacketOnlyIPv6DO(basic.DataPlaneOnly):
    """
    Just send an IPv6 packet with DO EH thru the switch
    """
    def runTest(self):
        
        pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrDestOpt()) 
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        pa_logger.info("Sending IPv6 packet with DOEH to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))

class PacketOnlyIPv6HBHandDO(basic.DataPlaneOnly):
    """
    Just send an IPv6 packet with HBHandDO EHs thru the switch
    """
    def runTest(self):
        
        pkt = simple_ipv6_packet(EH = True,  EHpkt = scapy.IPv6ExtHdrHopByHop()/scapy.IPv6ExtHdrDestOpt()) 
        of_ports = pa_port_map.keys()
        of_ports.sort()
        ing_port = of_ports[0]
        pa_logger.info("Sending IPv6 packet with HBHandDO EHs to " + str(ing_port))
        pa_logger.debug("Data: " + str(pkt).encode('hex'))
        self.dataplane.send(ing_port, str(pkt))


# Receive and verify pkt
# testutils.receive_pkt_verify(self, egr_port, exp_pkt)

if __name__ == "__main__":
    print "Please run through oft script:  ./oft --test-spec=ipv6"
