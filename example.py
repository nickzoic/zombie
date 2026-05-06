import zombie.server
import time

class Application:

    def __init__(self, send_queue):
        self.send_queue = send_queue

    def recv(self, msg):
        print(msg)

    def run(self):
        for i in range(0,10):
            self.send_queue.put("document.body.textContent = %d" % i)
            time.sleep(1)
        self.send_queue.shutdown()


zombie.server.serve(Application)
