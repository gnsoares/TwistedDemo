from queue import Queue


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
        print(f'Call {id} received')

        operator = self.get_available_operator()
        if operator is not None:
            self.call_to_operator(operator)
        else:
            print(f'Call {id} waiting in queue')

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

            print(f'Call {call.id} ringing for operator {operator.id}')

    def answer(self, id):

        operator = self.operator_table.get(id, None)

        if operator is not None:
            call = operator.call
            operator.state = 'busy'

            print(f'Call {call.id} answered by operator {operator.id}')

    def reject(self, id):

        operator = self.operator_table.get(id, None)

        if operator is not None:
            call = operator.call
            operator.state = 'available'
            call.operator = None

            print(f'Call {call.id} rejected by operator {operator.id}')

            self.put_call(call)
            self.call_to_operator(operator)

    def hangup(self, id):
        call = self.call_table.pop(id, None)

        if call is not None:
            operator = call.operator

            if operator is not None and operator.state == 'busy':
                print(f'Call {call.id} finished and operator {operator.id} available')
            else:
                print(f'Call {call.id} missed')

            if operator is not None:
                operator.state = 'available'
                self.call_to_operator(operator)
