import uuid
import time

def generate_uuid():
    return uuid.uuid1(node=0x1, clock_seq=int(time.time() * 100000)).hex[:10]
