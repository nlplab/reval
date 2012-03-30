'''
Common classes and functions.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-07
'''


class Textbound(object):
    def __init__(self, _id, _type, start, end, comment):
        self.id = _id
        self.type = _type
        self.start = start
        self.end = end
        self.comment = comment

    def __str__(self):
        return '{}\t{} {} {}\t{}'.format(self.id, self.type, self.start,
                self.end, self.comment)

    def __contains__(self, index):
        return self.start <= index < self.end


class Event(object):
    def __init__(self, _id, _type, trigger, args):
        self.id = _id
        self.type = _type
        self.trigger = trigger
        self.args = args

    def __str__(self):
        return '{}\t{}:{}{}'.format(self.id, self.type, self.trigger,
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
