

import logging

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Protocol, ReconnectingClientFactory

import stomper

stomper.utils.log_init(logging.DEBUG)

class StompProtocol(Protocol, stomper.Engine):

    def __init__(self, channel='', message='', username='', password=''):
        stomper.Engine.__init__(self)
        self.channel = channel
        self.message = message
        self.username = username
        self.password = password
        self.counter = 1
        self.log = logging.getLogger("sender")


    def connected(self, msg):
        """Once I've connected I want to subscribe to my the message queue.
        """
        stomper.Engine.connected(self, msg)

        self.log.info("Connected: session %s. Begining say hello." % msg['headers']['session'])
#         lc = LoopingCall(self.send)
#         lc.start(1)

        self.send("WHY HELLO!")

        f = stomper.Frame()
        f.unpack(stomper.subscribe(self.channel))

        # ActiveMQ specific headers:
        #
        # prevent the messages we send comming back to us.
        f.headers['activemq.noLocal'] = 'true'

        return f.pack()


    def ack(self, msg):
        """Processes the received message. I don't need to
        generate an ack message.

        """
        self.log.info("SENDER - received: %s " % msg['body'])
        return stomper.NO_REPONSE_NEEDED


    def send(self, msg):
        """Send out a hello message periodically.
        """
        self.log.info("Saying hello (%d)." % self.counter)

        f = stomper.Frame()
        f.unpack(stomper.send(self.channel, self.message))

        self.counter += 1

        # ActiveMQ specific headers:
        #
        #f.headers['persistent'] = 'true'

        self.transport.write(f.pack())

        self.transport.loseConnection()

    def connectionMade(self):
        """Register with stomp server.
        """
        cmd = stomper.connect(self.username, self.password)
        self.transport.write(cmd)


    def dataReceived(self, data):
        """Data received, react to it and respond if needed.
        """
        msg = stomper.unpack_frame(data)

        returned = self.react(msg)
        if returned:
            self.transport.write(returned)

class StompClientFactory(ReconnectingClientFactory):

    # Will be set up before the factory is created.
    username, password, message = '', '', ''

    def buildProtocol(self, addr):
        return StompProtocol(self.channel, self.message, self.username, self.password)

    def clientConnectionLost(self, connector, reason):
        """Lost connection
        """
        print 'Lost connection.  Reason:', reason
        reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        """Connection failed
        """
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        reactor.stop()

def start(game_id, host='localhost', port=61613, username='', password=''):
    """Start twisted event loop and the fun should begin...
    """
    StompClientFactory.username = username
    StompClientFactory.password = password
    StompClientFactory.message = 'message'
    StompClientFactory.channel = '/home/cjh/' + game_id

    reactor.connectTCP(host, port, StompClientFactory())
    reactor.run()

if __name__ == '__main__':
    start('hmmm')

