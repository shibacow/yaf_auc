import time
import logging
logging.basicConfig(level=logging.DEBUG)

def time_profile(func):
    def inner_func(*args,**kwargs):
        start=time.time()
        r=func(*args,**kwargs)
        end = time.time()
        spent=(end-start)
        msg="func={} time={}".format(func.__name__,spent)
        logging.info(msg)
        return r
    return inner_func

