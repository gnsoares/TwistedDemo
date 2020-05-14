import cmd
import json
import re
from sys import stdout

from twisted.internet import reactor, stdio
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
        self.transport.write(b'Client connected\n>>> ')

    def dataReceived(self, data):

        command_pattern = re.compile(r'(call|answer|reject|hangup) .*')
        response_pattern = re.compile(r'{"response": ".*"}')
        mc = command_pattern.match(data.decode('utf-8'))
        mr = response_pattern.match(data.decode('utf-8'))

        if mc is not None:
            self.cmd_interpreter.onecmd(mc.group(0))

        if mr is not None:
            lines = mr.group(0).split('}')
            for line in lines[:-1]:
                self.processResponse(line + '}')

    def processResponse(self, json_str):
        r = json.loads(json_str)
        print(r['response'] + '\n>>> ', end='')

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
    cmd_interpreter = CommandInterpreter()
    factory = CommandInterpreterFactory(cmd_interpreter)
    stdio.StandardIO(CommandInterpreterProtocol(cmd_interpreter))
    reactor.connectTCP(host, port, factory)
    reactor.run()
