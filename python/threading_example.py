from random import randrange
import threading
import sleep, Queue

class kartik(threading.Thread):

    def __init__(self, something ):
        threading.Thread.__init__(self)
        self.name = something

    def dummy(self):
        time.sleep(randrange(0,100))
        print("{} am awake and out".format(self.name))

    def run(self):
        self.dummy()

myl = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']

workers = Queue.Queue()

for i in myl:
    cond = True
    kart = kartik(i)
    if workers.qsize() < 3:
        workers.put(kart)
        kart.start()
    else:
        while cond:
            for i in range(0, len(workers.queue)):
                if not workers.queue[i].isAlive():
                    workers.queue.remove(workers.queue[i])
                    workers.put(kart)
                    kart.start()
                    cond = False
                    break
