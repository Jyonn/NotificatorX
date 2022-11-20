import hashlib


def md5(s):
    """获取字符串的MD5"""
    md5_ = hashlib.md5()
    md5_.update(s.encode())
    return md5_.hexdigest()


def sha1(s):
    sha1_ = hashlib.sha1()
    sha1_.update(s.encode())
    return sha1_.hexdigest()
