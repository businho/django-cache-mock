import threading


class Thread(threading.Thread):
    def run(self):
        self.exc = None
        try:
            super().run()
        except BaseException as exc:
            self.exc = exc

    def join(self):
        threading.Thread.join(self)
        if self.exc:
            raise self.exc
