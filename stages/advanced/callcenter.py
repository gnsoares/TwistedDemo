from queue import Queue
import json
from sys import stdout


from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor


class Operator():
    def __init__(self, id, state='available'):
        self.id = id
        self.state = state
        self.call = None

class Call():
    def __init__(self, id):
        self.id = id
        self.operator = None


class CallCenter():

    def __init__(self):
        self.call_id_queue = Queue()
        self.call_table = {}
        self.operator_table = {}

    def new_operator(self, id):

        operator = Operator(id)
        self.operator_table.update({id: operator})

        return operator

    def get_available_operator(self):

        for operator in self.operator_table.values():
            if operator.state == 'available':
                return operator
        else:
            return None

    def new_call(self, id):

        call = Call(id)
        self.put_call(call)
        message = f'Call {id} received\n'

        operator = self.get_available_operator()
        if operator is not None:
            attr_message = self.call_to_operator(operator)
            message += attr_message if attr_message is not None else ''
        else:
            message += f'Call {id} waiting in queue\n'

        return message

    def put_call(self, call):
        self.call_id_queue.put(call.id)
        self.call_table.update({call.id: call})        

    def pop_call(self):
        call = None
        while call is None and not self.call_id_queue.empty():
            call_id = self.call_id_queue.get()
            call = self.call_table.get(call_id, None)
        return call

    def call_to_operator(self, operator):

        call = self.pop_call()

        if call is not None:
            operator.state = 'ringing'
            operator.call = call

            call.operator = operator

            message = f'Call {call.id} ringing for operator {operator.id}\n'
        else:
            return None

        return message

    def answer(self, id):

        operator = self.operator_table.get(id, None)

        if operator is not None:
            call = operator.call
            operator.state = 'busy'

            message = f'Call {call.id} answered by operator {operator.id}\n'

        else:
            return None

        return message

    def reject(self, id):

        operator = self.operator_table.get(id, None)

        if operator is not None:
            call = operator.call
            operator.state = 'available'
            call.operator = None

            message = f'Call {call.id} rejected by operator {operator.id}\n'

            self.put_call(call)
            attr_message = self.call_to_operator(operator)
            message += attr_message if attr_message is not None else ''

        else:
            return None

        return message

    def hangup(self, id):
        call = self.call_table.pop(id, None)

        if call is not None:
            operator = call.operator

            if operator is not None and operator.state == 'busy':
                message = f'Call {call.id} finished and operator {operator.id} available\n'
            else:
                message = f'Call {call.id} missed\n'

            if operator is not None:
                operator.state = 'available'
                operator.call = None
                attr_message = self.call_to_operator(operator)
                message += attr_message if attr_message is not None else ''

        else:
            return None

        return message


class CallCenterProtocol(Protocol):
    
    def __init__(self, call_center):
        self.call_center = call_center

    def connectionMade(self):
        print("Hello, I'm server")

    def dataReceived(self, data):
        lines = data.split(b'}')
        for line in lines[:-1]:
            self.processCommand(line+b'}')

    def processCommand(self, json_str):
        try:
            r = json.loads(json_str)
            command = r['command']
            arg = r['id']
            if command == 'call':
                func = self.call_center.new_call
            elif command == 'answer':
                func = self.call_center.answer
            elif command == 'reject':
                func = self.call_center.reject
            elif command == 'hangup':
                func = self.call_center.hangup
            message = func(arg)
            print(message)
            json_str = json.dumps({"response": message})
            self.transport.write(json_str.encode('utf-8'))
        except:
            print(json_str)


class CallCenterFactory(Factory):

    def __init__(self, call_center):
        self.call_center = call_center

    def buildProtocol(self, addr):
        self.call_center.new_operator('A')
        self.call_center.new_operator('B')
        return CallCenterProtocol(self.call_center)


if __name__ == "__main__":
    endpoint = TCP4ServerEndpoint(reactor, 5678)
    endpoint.listen(CallCenterFactory(CallCenter()))
    reactor.run()