class Number(object):
    pass


class Str(object):
    pass


class Integer(Number):
    def __init__(self,len=11):
        self.len=len

    def __str__(self):
        return 'int({})'.format(self.len)


class Float(Number):
    def __str__(self):
        return 'float'


class Boolean(Number):
    def __str__(self):
        return 'BOOLEAN'


class String(Str):
    def __init__(self,length=255):
        self.length=length

    def __str__(self):
        return 'varchar({})'.format(self.length)


class Text(Str):
    def __str__(self):
        return 'text'


class Datetime(Str):
    def __str__(self):
        return 'datetime'

