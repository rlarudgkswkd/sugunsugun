import TrainAndTest

class Executer:
    def __init__(self, tcpServer):
        self.andRaspTCP = tcpServer
 
    def startCommand(self, command):
        if command == "456\n":
            #str = TrainAndTest.main()
            str = ""
            self.andRaspTCP.sendAll(TrainAndTest.main() + "\n")

