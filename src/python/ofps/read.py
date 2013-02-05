import xml.etree.ElementTree as et
from ncclient import manager 
import sys, getopt#, os


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

def getFullRoadmName(tag):
    return "{http://cpqd.com.br/drc/gso/ng/roadm/interface}%s" % (tag)

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

def readFromConfd(host, port, user, passwd, datafilter):
    with getSession(host, port, user, passwd) as m:
        return m.get_config(source='running', filter=datafilter).data_xml

# def main(argv):
    # """readConfig('127.0.0.1', 2022, 'admin', 'admin')"""
    # writeToConfd('127.0.0.1', 2022, 'admin', 'admin', templateCE)


# if __name__ == "__main__":
#     main(sys.argv[1:])
#     sys.exit(0)