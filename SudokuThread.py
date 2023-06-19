from threading import Thread, Semaphore

class SudokuThread(Thread):
    def __init__(self, lock: Semaphore, finished_lock: Semaphore, id,target = None,  args = None) -> None:
        self.lock = lock
        self.finished_lock = finished_lock
        self.result = None
        self.running = False
        self.idd = id
        super().__init__(target=target, args=args)
    
    def run(self):
        self.running = True
        while self.running:
            self.lock.acquire() # espera que a thread principal passe outra função para essa thread executar
            if self._target is not None:
                self.result = self._target(*self._args)
            else:
                self.result = None
            
            self.finished_lock.release() # notifica a thread principal que a função executada terminou


    def reset(self, target, args): #chamada pela thread principal após o termino da execução de uma função
        self._target = target
        self._args = args
        self.result = None
    
    def stop(self):
        self.running = False
        self._target = None
        self.lock.release()
