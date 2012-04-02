#!/usr/bin/env python

'''
Convert "standard" BioNLP Shared Task stand-off annotations into canonical
non-textbound annotations.

Author:     Pontus Stenetorp    <pontus stenetorp se>
Version:    2012-03-30
'''

from argparse import ArgumentParser, FileType
from itertools import combinations
from re import compile as re_compile
from sys import stderr, stdin, stdout
from collections import defaultdict, OrderedDict

### Constants
ARGPARSER = ArgumentParser()#XXX:
ARGPARSER.add_argument('-i', '--input', type=FileType('r'), default=stdin)
ARGPARSER.add_argument('-o', '--output', type=FileType('w'), default=stdout)
ARGPARSER.add_argument('-d', '--debug', action='store_true')
TRAILING_DIGIT_REGEX=re_compile('^.*(?P<digit>[0-9]+)$')
###

from lib.canoncommon import Text, Event, Modifier, Equiv
from lib.sort import sort_nicely

def _replace_ids(can_anns, _from, to, excluded_anns=None, debug=False):
    if excluded_anns is None:
        excluded_anns = set()
    for can_ann in can_anns:
        if isinstance(can_ann, Text) and Text not in excluded_anns:
            # These annotations can not reference others, pass
            pass
        elif isinstance(can_ann, Event) and Event not in excluded_anns:
            can_ann.args = [(a, to if v in _from else v)
                    for a, v in can_ann.args]
        elif isinstance(can_ann, Modifier) and Modifier not in excluded_anns:
            if can_ann.target in _from:
                can_ann.target = to
        elif isinstance(can_ann, Equiv) and Equiv not in excluded_anns:
            if debug:
                print >> stderr, 'Will purge from equiv:', _from & set(can_ann.members), to
            new_members = [m for m in can_ann.members if m not in _from]
            if new_members != can_ann.members:
                can_ann.members = new_members
                can_ann.members.append(to)
            sort_nicely(can_ann.members)
        elif not any(isinstance(can_ann, c) for c in (Text, Event, Modifier,
                    Equiv, )):
            assert False, 'unknown canonical annotation type'

# TODO: Pseudo-code for the conversion
def _st_to_canon(st_anns, debug=False):
    # Convert each known shared-task annotation type into the corresponding
    #    canonical annotation type
    can_anns = [a.to_can() for a in st_anns]
    if debug:
        print >> stderr, 'We start with', len(can_anns), 'canonical annotations'

    #for a in can_anns:
    #    print a
    #print
   
    # For later look-ups
    id_to_ann = {}
    for ann in can_anns:
        try:
            id_to_ann[ann.id] = ann
        except AttributeError, e:
            # Um, can we do this more cleanly?
            if not e.message.endswith(" object has no attribute 'id'"):
                raise

    # Find texts that are indistuiguishable without reference to their span
    equivalent_texts = defaultdict(set)
    text_anns = tuple([a for a in can_anns if isinstance(a, Text)])
    for text_ann in text_anns:
        for other_text_ann in (a for a in text_anns if a != text_ann):
            if (text_ann.text == other_text_ann.text
                    and text_ann.type == other_text_ann.type):
                equivalent_texts[(text_ann.text, text_ann.type)].add(text_ann.id)
                equivalent_texts[(other_text_ann.text, other_text_ann.type)].add(other_text_ann.id)
                #equivalent_texts[text_ann.text].add(text_ann.id)
                #equivalent_texts[other_text_ann.text].add(other_text_ann.id)
    #print >> stderr, equivalent_texts
    # Originally the equivalences are contextual, removing the context
    #   requires us to merge them
    eq_anns_to_remove = set()
    eq_anns = [a for a in can_anns if isinstance(a, Equiv)]
    for eq_set in equivalent_texts.itervalues():
        #print 'EQ:', eq_set
        #print eq_anns
        for eq_ann_a, eq_ann_b in combinations(eq_anns, 2):
            #print 'A:', eq_ann_a.members
            #print 'B:', eq_ann_b.members
            # Does the equivalent texts bridge the equivalences?
            if ((set(eq_ann_a.members) & eq_set)
                    and (set(eq_ann_b.members) & eq_set)):
                if debug:
                    print >> stderr, 'Merging:', eq_ann_a, 'and', eq_ann_b
                eq_ann_a.members = eq_ann_a.members + [a for a in eq_ann_b.members
                        if a not in eq_ann_a.members]
                sort_nicely(eq_ann_a.members)
                eq_ann_b.members = eq_ann_b.members + [a for a in eq_ann_a.members
                        if a not in eq_ann_b.members]
                sort_nicely(eq_ann_b.members)
                # We can now safely remove the latter annotation later on
                eq_anns_to_remove.add(eq_ann_b)
    if debug and eq_anns_to_remove:
        print >> stderr, 'Will remove redundant Equivs:', eq_anns_to_remove
    can_anns = [a for a in can_anns if a not in eq_anns_to_remove]
    # Merge text into unique (texts, types) since we now lack textual bounds
    ids_to_remove = set()
    for eq_set in equivalent_texts.itervalues():
        eqs = [a for a in eq_set]
        sort_nicely(eqs)
        to_keep = eqs[0]
        not_to_keep = set(eq_set - set((to_keep, )))
        ids_to_remove = ids_to_remove | not_to_keep
        _replace_ids(can_anns, not_to_keep, to_keep, debug=debug)
    # Finally, remove the redundant annotations
    can_anns = [a for a in can_anns if not (hasattr(a, 'id')
            and a.id in ids_to_remove)]
    # Purge empty equivs
    can_anns = [a for a in can_anns if not (isinstance(a, Equiv)
            and not a.members)]

    # XXX:
    from collections import namedtuple
    EventArg = namedtuple('EventArg', ('type', 'id', 'text', ))
    # XXX:
    
    # For consistency we pair and sort event arguments
    for e_ann in (a for a in can_anns if isinstance(a, Event)):
        # Pair all arguments into sorted related groups
        arg_num_to_args = {}
        for _type, _id in e_ann.args:
            #assert any(_type.startswith(t) for t in ('Theme', 'Site', 'Cause', 'CSite', 'AtLoc', 'ToLoc', )), _type #XXX:
            try:
                text = id_to_ann[_id].text
            except AttributeError:
                # Most likely an event annotation
                text=None
                #text = id_to_ann[id_to_ann[_id].trigger].text
            e_arg = EventArg(type=_type, id=_id, text=text)
            match = TRAILING_DIGIT_REGEX.match(e_arg.type)
            if match is not None:
                arg_num = int(match.groupdict()['digit'])
            else:
                arg_num = 1

            try:
                arg_num_to_args[arg_num].append(e_arg)
                arg_num_to_args[arg_num].sort(key=lambda x : x.type)
            except KeyError:
                arg_num_to_args[arg_num] = [e_arg, ]

        # Rebuild the event arguments
        e_ann.args = []
        for k in sorted(k for k in arg_num_to_args):
            for arg in arg_num_to_args[k]:
                e_ann.args.append((arg.type, arg.id, ))

    # We will select a single surface form for all annotations, not strictly
    #       necesarry but makes manual analysis easier
    for eq_ann in (a for a in can_anns if isinstance(a, Equiv)):
        sforms = [(id_to_ann[_id].text, _id) for _id in eq_ann.members]
        sforms.sort()
        can_form = sforms[-1][1]
        other_forms = [_id for _, _id in sforms][:-1]
        _replace_ids(can_anns, other_forms, can_form,
                excluded_anns=set((Equiv, )), debug=debug)

    for can_ann in can_anns:
        yield can_ann

from lib.stann import parse_st_ann

def main(args):
    argp = ARGPARSER.parse_args(args[1:])

    # Parse the old shared-task annotations
    st_anns = (a for a in parse_st_ann(l.rstrip('\n') for l in argp.input))

    canon_ann_i = None
    for canon_ann_i, canon_ann in enumerate(
            _st_to_canon(st_anns, debug=argp.debug)):
        argp.output.write(unicode(canon_ann))
        argp.output.write('\n')
    if canon_ann_i is None:
        # Blank input...
        # TODO: Do this catch nicer!
        argp.output.write('\n')
    return 0

if __name__ == '__main__':
    from sys import argv
    exit(main(argv))
