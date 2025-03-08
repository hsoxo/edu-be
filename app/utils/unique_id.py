import nanoid


def get_id(length: int = 8):
    return nanoid.generate("1234567890abcdefghijklmnopqrstuvwxyz", size=length)
