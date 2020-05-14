import cmd
import json
from sys import stdout

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory


class CommandInterpreter(cmd.Cmd):

    # ----- commands -----
    def do_call(self, arg):
        'makes application receive a call whose id is ​ <arg>​ '

        json_str = json.dumps({"command": "call", "id": arg})
        self.protocol.sendCommand(json_str)

    def do_answer(self, arg):
        'makes operator ​<arg>​ answer a call being delivered to it'

        json_str = json.dumps({"command": "answer", "id": arg})
        self.protocol.sendCommand(json_str)

    def do_reject(self, arg):
        'makes operator ​<arg>​ reject a call being delivered to it'

        json_str = json.dumps({"command": "reject", "id": arg})
        self.protocol.sendCommand(json_str)

    def do_hangup(self, arg):
        'makes call whose ​id is <arg> be finished​'

        json_str = json.dumps({"command": "hangup", "id": arg})
        self.protocol.sendCommand(json_str)

    def do_exit(self, arg):
        return True


class CommandInterpreterProtocol(Protocol):

    def __init__(self, cmd_interpreter):
        self.cmd_interpreter = cmd_interpreter
        self.cmd_interpreter.protocol = self

    def connectionMade(self):
        reactor.callInThread(self.cmd_interpreter.cmdloop)
        print("Hello, I'm client")

    def dataReceived(self, data):
        lines = data.split(b'}')
        for line in lines[:-1]:
            self.processResponse(line+b'}')

    def processResponse(self, json_str):
        r = json.loads(json_str)
        print(r['response'])

    def sendCommand(self, json_str):
        self.transport.write(json_str.encode('utf-8'))

class CommandInterpreterFactory(ClientFactory):

    def __init__(self, cmd_interpreter):
        self.cmd_interpreter = cmd_interpreter

    def buildProtocol(self, addr):
        p = CommandInterpreterProtocol(self.cmd_interpreter)
        p.factory = self
        return p

if __name__ == "__main__":
    host = "localhost"
    port = 5678
    factory = CommandInterpreterFactory(CommandInterpreter())
    reactor.connectTCP(host, port, factory)
    reactor.run()
