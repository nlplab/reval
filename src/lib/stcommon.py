'''
Common classes and functions for the shared-task annotation format.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-07
'''

from canoncommon import (Text, Event as CanEvent, Modifier as CanModifier,
        Equiv as CanEquiv)


class Textbound(object):
    def __init__(self, _id, _type, start, end, comment):
        self.id = _id
        self.type = _type
        self.start = start
        self.end = end
        self.comment = comment

    def to_can(self):
        return Text(self.id, self.type, self.comment)

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

    def to_can(self):
        return CanEvent(self.id, self.type, self.args)

    def __str__(self):
        return '{}\t{}:{}{}'.format(self.id, self.type, self.trigger,
                (' ' + ' '.join('{}:{}'.format(a, v)
                    for a, v in self.args)) if self.args else '')


class Modifier(object):
    def __init__(self, _id, _type, target):
        self.id = _id
        self.type = _type
        self.target = target

    def to_can(self):
        # Really identical, but it is better to keep them seperate
        return CanModifier(self.id, self.type, self.target)

    def __str__(self):
        return '{}\t{} {}'.format(self.id, self.type, self.target)


class Equiv(object):
    def __init__(self, members):
        self.members = members

    def to_can(self):
        # Really identical, but it is better to keep them seperate
        return CanEquiv(self.members)

    def __str__(self):
        return '*\tEquiv {}'.format(' '.join(self.members))
