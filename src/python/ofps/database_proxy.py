import xml.etree.ElementTree as et
from ncclient import manager 
import sys, getopt#, os
# import oftest.cstruct as ofp
import ofp

templateDeleteCC = """
<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ns1="http://cpqd.com.br/chassis/system" xmlns:ns2="http://cpqd.com.br/roadm/system"> 
  <ns1:config>
    <ns1:system>
      <ns2:roadm>
        <ns2:cross-connections>
          <ns2:cross-connection xc:operation="delete">
            <ns2:cc-label>%s</ns2:cc-label>
            <ns2:cc-channel>%s</ns2:cc-channel>
            <ns2:in>%s</ns2:in>
            <ns2:out>%s</ns2:out>
          </ns2:cross-connection>
        </ns2:cross-connections>
      </ns2:roadm>
    </ns1:system>
  </ns1:config>
</config>
"""

templateCE = """
<config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:ns1="http://cpqd.com.br/chassis/system" xmlns:ns2="http://cpqd.com.br/roadm/system"> 
  <ns1:config>
    <ns1:system>
      <ns2:roadm>
        <ns2:cross-connections>
          <ns2:cross-connection>
            <ns2:cc-label>%s</ns2:cc-label>
            <ns2:cc-channel>%s</ns2:cc-channel>
            <ns2:in>%s</ns2:in>
            <ns2:out>%s</ns2:out>
          </ns2:cross-connection>
        </ns2:cross-connections>
      </ns2:roadm>
    </ns1:system>
  </ns1:config>
</config>
"""

def getAllPorts(host, port, user, passwd):
    datafilter = datafilter = ("xpath","/config/system/roadm/wdm-interface")
    config = readFromConfd(host, port, user, passwd, datafilter)
    root = et.fromstring(config)
    all_ports = {}
    name_to_port = {}
    j = 1
    all_ports[0] = '0'
    name_to_port['0'] = 0
    for k in root.iter(getFullInterfaceName('interface')):
        name = ''
        _type = ''
        
        for i in k.iter(getFullInterfaceName('name')):
            name = i.text
        for i in k.iter(getFullInterfaceName('type')):
            _type = i.text

        all_ports[j] = name
        name_to_port[name] = j
        # print "pairing of_port_no = " + str(j) + "  |  name = " + name
        j+=1

    all_ports[ofp.OFPP_ALL] = 'OFPP_ALL'
    name_to_port['OFPP_ALL'] = ofp.OFPP_ALL

    return all_ports , name_to_port

def getFlowStats(host, port, user, passwd):
    datafilter = ("xpath","/config/system/roadm/cross-connections")
    config = readFromConfd(host, port, user, passwd,  datafilter)
    root = et.fromstring(config)

    inp = switch.ports[msg.match.in_port].name
    outp = switch.ports[msg.out_port].name
    channel = str(msg.match.dl_vlan)

    replies = []

    for k in root.iter(getFullRoadmName('cross-connection')):
        rin = ''
        rout = ''
        rch = ''
        stats = []
        for i in k.iter(getFullRoadmName('in')):
            rin = i.text
        for i in k.iter(getFullRoadmName('out')):
            rout = i.text
        for i in k.iter(getFullRoadmName('cc-channel')):
            rch = i.text
        
        print 'checking:'
        print "in: %s out: %s channel: %s" % (rin, rout, rch)
        print 'against:'
        print "in: %s out: %s channel: %s" % (inp, outp, channel)

def getFullRoadmName(tag):
    return "{http://cpqd.com.br/drc/gso/ng/roadm/interface}%s" % (tag)

def getFullInterfaceName(tag):
    return "{http://cpqd.com.br/roadm/system}%s" % (tag)
    

def default_unknown_host_cb(host, key):
    return True

def getSession(host, port, user, password):
    m = manager.connect( host = host,
                         port = port,
                         username = user,
                         password = password,
                         unknown_host_cb = default_unknown_host_cb,
                         key_filename = None,
                         allow_agent = False,
                         look_for_keys = False )
    return m

def writeToConfd(host, port, user, passwd, cc_label, cc_channel, cc_in, cc_out):
    m = getSession(host, port, user, passwd)
    assert(":validate" in m.server_capabilities)
    snippet = templateCE % (cc_label, cc_channel, cc_in , cc_out)
    print snippet 
    m.edit_config(target='running', config=snippet,
                      test_option='test-then-set')

def deleteFromConfd(host, port, user, passwd, cc_label, cc_channel, cc_in, cc_out):
    m = getSession(host, port, user, passwd)
    assert(":validate" in m.server_capabilities)
    snippet = templateDeleteCC % (cc_label, cc_channel, cc_in , cc_out)
    # print snippet 
    m.edit_config(target='running', config=snippet,
                      test_option='test-then-set')

def readFromConfd(host, port, user, passwd, datafilter):
    with getSession(host, port, user, passwd) as m:
        return m.get_config(source='running', filter=datafilter).data_xml

def isCCAvailable(host, port, user, passwd, inp, outp, channel):
    datafilter = datafilter = ("xpath","/config/system/cross-connections")
    config = readFromConfd(host, port, user, passwd, datafilter)
    root = et.fromstring(config)
    
    for k in root.iter(getFullRoadmName('cross-connection')):
        rin = ''
        rout = ''
        rch = ''
        
        for i in k.iter(getFullRoadmName('in')):
            rin = i.text
        for i in k.iter(getFullRoadmName('out')):
            rout = i.text
        for i in k.iter(getFullRoadmName('channel')):
            rch = i.text
        
        print 'checking:'
        print "in: %s out: %s channel: %s" % (rin, rout, rch)
        print 'against:'
        print "in: %s out: %s channel: %s" % (inp, outp, channel)
        
        if (rin == inp) & (rout == outp) & (rch == channel):
            return False
    return True

# def main(argv):
    # """readConfig('127.0.0.1', 2022, 'admin', 'admin')"""
    # writeToConfd('127.0.0.1', 2022, 'admin', 'admin', templateCE)


# if __name__ == "__main__":
#     main(sys.argv[1:])
#     sys.exit(0)