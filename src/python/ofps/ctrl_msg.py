######################################################################
#
# All files associated with the OpenFlow Python Switch (ofps) are
# made available for public use and benefit with the expectation
# that others will use, modify and enhance the Software and contribute
# those enhancements back to the community. However, since we would
# like to make the Software available for broadest use, with as few
# restrictions as possible permission is hereby granted, free of
# charge, to any person obtaining a copy of this Software to deal in
# the Software under the copyrights without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
######################################################################
# import oftest.cstruct as ofp
import ofp
import ofp.message as message
from oftest import ofutils

"""
Functions to handle specific controller messages

The function name must match <message_name> where
message_name is from the oftest message list.  For example, 
features_request.

@todo Implement these functions
"""

from exec_actions import execute_actions
from oftest.packet import Packet

def aggregate_stats_reply(switch, msg, rawmsg):
    """
    Process an aggregate_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type aggregate_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received aggregate_stats_reply from controller")

def aggregate_stats_request(switch, msg, rawmsg):
    """
    Process an aggregate_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type aggregate_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received aggregate_stats_request from controller")

def bad_action_error_msg(switch, msg, rawmsg):
    """
    Process a bad_action_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type bad_action_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received bad_action_error_msg from controller")

def bad_request_error_msg(switch, msg, rawmsg):
    """
    Process a bad_request_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type bad_request_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received bad_request_error_msg from controller")

def barrier_reply(switch, msg, rawmsg):
    """
    Process a barrier_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type barrier_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received barrier_reply from controller")

def barrier_request(switch, msg, rawmsg):
    """
    Process a barrier_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type barrier_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received barrier_request from controller")
    b = message.barrier_reply()
    b.header.xid = msg.header.xid
    switch.controller.message_send(b)

def desc_stats_reply(switch, msg, rawmsg):
    """
    Process a desc_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type desc_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received desc_stats_reply from controller")
    
def desc_stats_request(switch, msg, rawmsg):
    """
    Process a desc_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type desc_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received desc_stats_request from controller")
    reply = switch.pipeline.desc_stats_get(msg, switch)
    if reply :
        switch.logger.debug("Sending desc_stats_reply from controller")
        switch.controller.message_send(reply)
    else:
        switch.logger.error("switch.pipeline.desc_stats_get() returned NONE !?")

def echo_reply(switch, msg, rawmsg):
    """
    Process an echo_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type echo_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received echo_reply from controller")

def echo_request(switch, msg, rawmsg):
    """
    Process an echo_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type echo_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received echo_request from controller")
    msg.header.type = ofp.OFPT_ECHO_REPLY
    switch.controller.message_send(msg, zero_xid=True)

def error(switch, msg, rawmsg):
    """
    Process an error message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type error
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received error from controller")

def experimenter(switch, msg, rawmsg):
    """
    Process an experimenter message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type experimenter
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received experimenter from controller")

def features_reply(switch, msg, rawmsg):
    """
    Process a features_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type features_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received features_reply from controller")

def features_request(switch, msg, rawmsg):
    """
    Process a features_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type features_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received features_request from controller")
    rep = message.features_reply()
    rep.header.xid = msg.header.xid
    rep.datapath_id = switch.config.getConfig('datapath_id')
    rep.n_buffers = 10000 #@todo figure out real number of buffers
    rep.n_tables = switch.config.n_tables
    # for now, list some simple things that we will likely (but don't yet) support
    rep.capabilities = ofp.OFPC_FLOW_STATS | ofp.OFPC_PORT_STATS | \
        ofp.OFPC_TABLE_STATS 
    rep.ports = switch.ports.values()
    switch.controller.message_send(rep)

import database_proxy as DataBaseP
import xml.etree.ElementTree as et

cc_instance_map = {
    
}

def flow_mod(switch, msg, rawmsg):
    """
    Process a flow_mod message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type flow_mod
    @param rawmsg The actual packet received as a string
    """

    if msg.command == ofp.OFPFC_ADD : 
        if msg.out_port in switch.ports.keys() and msg.match.in_port in switch.ports.keys() :
            cc_label = switch.ports[msg.match.in_port].name + '_' + switch.ports[msg.out_port].name + '_' + str(msg.match.dl_vlan)
            print "LABEL = " + cc_label
            DataBaseP.writeToConfd('127.0.0.1', 2022, 'admin', 'admin', cc_label, 
              str(msg.match.dl_vlan) , 
              switch.ports[msg.match.in_port].name, 
              switch.ports[msg.out_port].name)
            

    elif msg.command == ofp.OFPFC_DELETE or \
       msg.command == ofp.OFPFC_DELETE_STRICT :
        if msg.out_port in switch.ports.keys() and msg.match.in_port in switch.ports.keys() :
            cc_label = switch.ports[msg.match.in_port].name + '_' + switch.ports[msg.out_port].name + '_' + str(msg.match.dl_vlan)
            print "LABEL = " + cc_label
            DataBaseP.deleteFromConfd('127.0.0.1', 2022, 'admin', 'admin', cc_label, 
              str(msg.match.dl_vlan) , 
              switch.ports[msg.match.in_port].name, 
              switch.ports[msg.out_port].name)
            


    # if msg.out_port in port_to_name_map.keys() and  msg.match.in_port in port_to_name_map.keys()  \
    #    and cc_port_used[msg.out_port] == 0 and  cc_port_used[msg.match.in_port] == 0 :
    #     cc_label = port_to_name_map[msg.match.in_port] + '_' + port_to_name_map[msg.out_port] + '_' + str(msg.match.dl_vlan)
    #     print "LABEL = " + cc_label
    #     read_it.writeToConfd('127.0.0.1', 2022, 'admin', 'admin', cc_label, 
    #         str(msg.match.dl_vlan) , 
    #         port_to_name_map[msg.match.in_port], 
    #         port_to_name_map[msg.out_port])
    #     cc_port_used[msg.match.in_port] = 1
    #     cc_port_used[msg.out_port] = 1

    # else :
    # (rv, err_msg) = switch.pipeline.flow_mod_process(msg, switch.groups)
    # switch.logger.debug("Handled flow_mod, result: " + str(rv) + ", " +
    #                     "None" if err_msg is None else err_msg.__class__.__name__)
    # if rv !=  0:
    #     switch.controller.message_send(err_msg)

def flow_mod_failed_error_msg(switch, msg, rawmsg):
    """
    Process a flow_mod_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type flow_mod_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received flow_mod_failed_error_msg from controller")

def flow_removed(switch, msg, rawmsg):
    """
    Process a flow_removed message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type flow_removed
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received flow_removed from controller")

def flow_stats_reply(switch, msg, rawmsg):
    """
    Process a flow_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type flow_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received flow_stats_reply from controller")

def flow_stats_request(switch, msg, rawmsg):
    """
    Process a flow_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type flow_stats_request
    @param rawmsg The actual packet received as a string
    """
    
    datafilter = ("xpath","/config/system/roadm/cross-connections")
    config = DataBaseP.readFromConfd('127.0.0.1', 2022, 'admin', 'admin',  datafilter)
    root = et.fromstring(config)

    inp = switch.ports[msg.match.in_port].name
    outp = switch.ports[msg.out_port].name
    channel = str(msg.match.dl_vlan)

    replies = []

    for k in root.iter(DataBaseP.getFullInterfaceName('cross-connection')):
        rin = ''
        rout = ''
        rch = ''
        stats = []
        for i in k.iter(DataBaseP.getFullInterfaceName('in')):
            rin = i.text
        for i in k.iter(DataBaseP.getFullInterfaceName('out')):
            rout = i.text
        for i in k.iter(DataBaseP.getFullInterfaceName('cc-channel')):
            rch = i.text
        
        print 'checking:'
        print "in: %s out: %s channel: %s" % (rin, rout, rch)
        print 'against:'
        print "in: %s out: %s channel: %s" % (inp, outp, channel)
        if (rin == inp) & (rout == outp or outp == switch.ports[ofp.OFPP_ALL].name) & (rch == channel) :
            stat = message.flow_stats_entry()
            stat.match.in_port = msg.match.in_port
            stat.match.dl_vlan = msg.match.dl_vlan
            output = action.output()
            output.port = name_to_port[rout]
            stat.actions.append(output)

            replies.append(stat)

        elif (inp == switch.ports[0].name or (msg.match.wildcards & ofp.OFPFW_IN_PORT == ofp.OFPFW_IN_PORT)) and (outp == switch.ports[ofp.OFPP_ALL].name) and (channel == '0' or msg.wildcards & ofp.OFPFW_DL_VLAN == ofp.OFPFW_DL_VLAN):
            print "Add response : "
            stat = message.flow_stats_entry()

            stat.match.in_port = switch.name_to_port[rin]
            stat.match.dl_vlan = int(rch)
            output = ofp.action.output()
            output.port = switch.name_to_port[rout]
            stat.actions.add(output)

            replies.append(stat)
    
    reply = message.flow_stats_reply()
    reply.header.xid = msg.header.xid
    reply.stats = replies
    switch.logger.debug("Sending flow_stats_response to controller")    
    switch.controller.message_send(reply)
    

    # switch.logger.debug("Received flow_stats_request from controller")
    # reply = switch.pipeline.flow_stats_get(msg,switch.groups)
    # if not reply : 
    #     switch.logger.error("Got None reply from switch.pipeline.flow_stats_get(); dropping request")
    # else:
    #     switch.logger.debug("Sending flow_stats_response to controller")
    #     switch.controller.message_send(reply)

def get_config_reply(switch, msg, rawmsg):
    """
    Process a get_config_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type get_config_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received get_config_reply from controller")

def get_config_request(switch, msg, rawmsg):
    """
    Process a get_config_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type get_config_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received get_config_request from controller")

def group_desc_stats_request(switch, msg, rawmsg):
    """
    Process a group_desc_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type group_desc_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received group_desc_stats_request from controller")

def group_desc_stats_reply(switch, msg, rawmsg):
    """
    Process a group_desc_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type group_desc_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received group_desc_stats_reply from controller")

def group_stats_request(switch, msg, rawmsg):
    """
    Process a group_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type group_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received group_stats_request from controller")

def group_stats_reply(switch, msg, rawmsg):
    """
    Process a group_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type group_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received group_stats_reply from controller")

def group_mod(switch, msg, rawmsg):
    """
    Process a group_mod message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type group_mod
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received group_mod from controller")
    switch.groups.update(msg)

def group_mod_failed_error_msg(switch, msg, rawmsg):
    """
    Process a group_mod_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type group_mod_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received group_mod_failed_error_msg from controller")

def hello(switch, msg, rawmsg):
    """
    Process a hello message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type hello
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received hello from controller")

def hello_failed_error_msg(switch, msg, rawmsg):
    """
    Process a hello_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type hello_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received hello_failed_error_msg from controller")

def packet_in(switch, msg, rawmsg):
    """
    Process a packet_in message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type packet_in
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received packet_in from controller")

def packet_out(switch, msg, rawmsg):
    """
    Process a packet_out message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type packet_out
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received packet_out from controller")
    packet = Packet(in_port=msg.in_port, data=msg.data)
    switch.logger.debug("Executing action list")
    print msg.actions.show()
    execute_actions(switch, packet, msg.actions)

def port_mod(switch, msg, rawmsg):
    """
    Process a port_mod message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type port_mod
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received port_mod from controller")
    err = None
    try:
        port = switch.ports[msg.port_no]
        if port.hw_addr == msg.hw_addr:
            port.config = (port.config& ~msg.mask) | (msg.config & msg.mask)
            if msg.advertise != 0 :
                port.advertise = msg.advertise
                #@todo check to see if requested features is valid
                #@todo throw an error if invalid : 
                #        http://www.openflow.org/bugs/openflow/ticket/249
                port.curr = port.advertise
                #@todo update port.curr and call to ioctl() to actually change
                #the port's speed
        else:
            err =  ofutils.of_error_msg_make(ofp.OFPET_PORT_MOD_FAILED, ofp.OFPPMFC_BAD_HW_ADDR, msg)
    except IndexError:
        switch.logger.error("port_mod from controller tried to access non-existent" + 
                            " port %d %x:%x:%x:%x%x:%x" % ((msg.port) + msg.hw_addr ))
        err = ofutils.of_error_msg_make(ofp.OFPET_PORT_MOD_FAILED, ofp.OFPPMFC_BAD_PORT, msg)
    if err:
        switch.controller.message_send(err)

def port_mod_failed_error_msg(switch, msg, rawmsg):
    """
    Process a port_mod_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type port_mod_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received port_mod_failed_error_msg from controller")

def port_stats_reply(switch, msg, rawmsg):
    """
    Process a port_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type port_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received port_stats_reply from controller")

def port_stats_request(switch, msg, rawmsg):
    """
    Process a port_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type port_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received port_stats_request from controller")

def port_status(switch, msg, rawmsg):
    """
    Process a port_status message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type port_status
    @param rawmsg The actual packet received as a string
    
    @warning: For clarity; controllers should NEVER send port_status msgs
           they only send port_mod msgs.   
    """
    switch.logger.debug("Received port_status from controller")

def queue_get_config_reply(switch, msg, rawmsg):
    """
    Process a queue_get_config_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type queue_get_config_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received queue_get_config_reply from controller")

def queue_get_config_request(switch, msg, rawmsg):
    """
    Process a queue_get_config_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type queue_get_config_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received queue_get_config_request from controller")

def queue_op_failed_error_msg(switch, msg, rawmsg):
    """
    Process a queue_op_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type queue_op_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received queue_op_failed_error_msg from controller")

def queue_stats_reply(switch, msg, rawmsg):
    """
    Process a queue_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type queue_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received queue_stats_reply from controller")

def queue_stats_request(switch, msg, rawmsg):
    """
    Process a queue_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type queue_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received queue_stats_request from controller")

def set_config(switch, msg, rawmsg):
    """
    Process a set_config message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type set_config
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received set_config from controller")

def switch_config_failed_error_msg(switch, msg, rawmsg):
    """
    Process a switch_config_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type switch_config_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received switch_config_failed_error_msg from controller")

# def table_mod(switch, msg, rawmsg):
#     """
#     Process a table_mod message from the controller
#     @param switch The main switch object
#     @param msg The parsed message object of type table_mod
#     @param rawmsg The actual packet received as a string
#     """
#     switch.logger.debug("Received table_mod from controller")
#     error = switch.pipeline.table_mod_process(msg)
#     if error :
#         switch.controller.message_send(error)

def table_mod_failed_error_msg(switch, msg, rawmsg):
    """
    Process a table_mod_failed_error_msg message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type table_mod_failed_error_msg
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received table_mod_failed_error_msg from controller")

def table_stats_reply(switch, msg, rawmsg):
    """
    Process a table_stats_reply message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type table_stats_reply
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received table_stats_reply from controller")

def table_stats_request(switch, msg, rawmsg):
    """
    Process a table_stats_request message from the controller
    @param switch The main switch object
    @param msg The parsed message object of type table_stats_request
    @param rawmsg The actual packet received as a string
    """
    switch.logger.debug("Received table_stats_request from controller")
    reply = switch.pipeline.table_stats_get(msg)
    if reply :
        switch.logger.debug("Sending table_stats_reply")
        switch.controller.message_send(reply)
    else:
        switch.logger.debug("Got NONE from pipeline.table_stats_get()!?")
