import uuid
import time


def generate_uuid():
    return str(uuid.uuid4()).replace("-", "")[0:10]
