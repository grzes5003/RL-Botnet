import psutil


class Env:

    n = 4

    @staticmethod
    def cpu_usage():
        return psutil.cpu_percent()

    @staticmethod
    def ram_usage():
        return psutil.virtual_memory().percent

    @staticmethod
    def net_packets():
        return psutil.net_io_counters().packets_sent,\
            psutil.net_io_counters().packets_recv

    @staticmethod
    def net_bytes():
        return psutil.net_io_counters().bytes_sent,\
            psutil.net_io_counters().bytes_recv

    @staticmethod
    def get_env():
        return Env.cpu_usage(), Env.ram_usage(), Env.net_packets(), Env.net_bytes()

    @staticmethod
    def sample():
        pass

    @staticmethod
    def step(action):
        pass

    @staticmethod
    def reset():
        pass
