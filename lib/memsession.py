import memcache 
from conf import config

class MemcacheStore():
    def __init__(self, server=config.memcache.server, timeout=config.memcache.timeout):
#    def __init__(self, server=['127.0.0.1:11211'],timeout=0):
        self.mc = memcache.Client(server, debug=False)
        self.timeout = timeout

    def __contains__(self, key):
        return True if self.mc.get(key) else False

    def __getitem__(self, key):
        return self.mc.get(key)

    def __setitem__(self, key, value):
        self.mc.set(key, value, self.timeout)

    def __delitem__(self, key):
        self.mc.delete(key)

    def cleanup(self, timeout):
        pass


