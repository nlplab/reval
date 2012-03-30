'''
Common classes and functions for our canonical annotation format.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-30
'''


class Text(object):
    def __init__(self, _id, _type, text):
        self.id = _id
        self.type = _type
        self.text = text

    def __str__(self):
        return '{}\t{}\t{}'.format(self.id, self.type, self.text)


class Event(object):
    def __init__(self, _id, _type, trigger, args):
        self.id = _id
        self.type = _type
        self.args = args

    def __str__(self):
        return '{}\t{}{}'.format(self.id, self.type,
                (' ' + ' '.join('{}:{}'.format(a, v)
                    for a, v in self.args)) if self.args else '')


class Modifier(object):
    def __init__(self, _id, _type, target):
        self.id = _id
        self.type = _type
        self.target = target

    def __str__(self):
        return '{}\t{} {}'.format(self.id, self.type, self.target)


class Equiv(object):
    def __init__(self, members):
        self.members = members

    def __str__(self):
        return '*\tEquiv {}'.format(' '.join(self.members))
