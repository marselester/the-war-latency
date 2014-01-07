# coding: utf-8
from twisted.application import internet, service

from the_war_latency.protocols import WarFactory


port = 6666
iface = 'localhost'
application = service.Application('The War: Latency')

factory = WarFactory()
tcp_service = internet.TCPServer(port, factory, interface=iface)
tcp_service.setServiceParent(application)
