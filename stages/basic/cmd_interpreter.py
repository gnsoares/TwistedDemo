import cmd
import json

from callcenter import CallCenter

class CommandInterpreter(cmd.Cmd):

    call_center = CallCenter()

    # ----- commands -----
    def do_register_operator(self, arg):
        'register a new operator with id <arg>'

        self.call_center.new_operator(arg)

    def do_call(self, arg):
        'makes application receive a call whose id is ​ <arg>​ '

        self.call_center.new_call(arg)

    def do_answer(self, arg):
        'makes operator ​<arg>​ answer a call being delivered to it'

        self.call_center.answer(arg)

    def do_reject(self, arg):
        'makes operator ​<arg>​ reject a call being delivered to it'

        self.call_center.reject(arg)


    def do_hangup(self, arg):
        'makes call whose ​id is <arg> be finished​'

        self.call_center.hangup(arg)

    def do_exit(self, arg):
        return True


if __name__ == "__main__":
    CommandInterpreter().cmdloop()