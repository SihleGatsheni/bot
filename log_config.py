import logging
class LogManager:
     
    def __init__(self) -> None:
        self.log = logging
        self.log.basicConfig(format="%(levelname)s:%(message)s")
    
def log(self):
    return self.log