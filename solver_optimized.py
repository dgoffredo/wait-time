# This Python file uses the following encoding: utf-8
'''
readable_input = [
    [ '0', '1', '2' ], # Slots are assumed to be numbered like this.
     ######
    [ 'a', 'b', 'c' ],
    [ 'b', 'a', 'd' ],
    [ 'c', 'd', 'b' ],
    [ '',  'c', 'a' ]
]
'''
'''
readable_input = [
    [ '0', '1' ],
    #####
    [ 'a', 'b' ],
    [ 'b', 'a' ]
]
'''
'''
readable_input = [
    [0, 1, 2, 3],
    ['1',''   ,''  ,''  ],
    ['2', ''  , '' ,''  ],
    ['3',  '' ,''  , '' ],
    ['4', ''  ,''  ,''  ],
    ['5',  '' , '' , '' ],
    ['6', ''  ,''  , '' ],
]
'''

import random
from scipy.optimize import fsolve
from time import time
def run_it():
    # Create a big system randomly
    ntickets = 20
    nslots = 25
    random_input = [ random.sample(['t%d' % i for i in range(1, ntickets+1)], random.randint(0, ntickets)) for _ in range(nslots) ]
    # for index, queue in enumerate(random_input):
        # print index, '-->', queue
    # print '-----------------'
    real_input = random_input
    '''
    real_input = zip(*readable_input[1:])
    # print real_input
    '''
    pairs = [(t, s) for s, queue in enumerate(real_input) for t in queue if len(t) > 0]
    # # print pairs

    values = []
    meta = {}
    running_index = 0
    for slot, queue in enumerate(real_input):
        for place, ticket in enumerate(queue):
            if len(ticket) == 0:
                continue

            wt = {
                'index': running_index,
                'deps': [('wc', t, slot) for t in queue[:place]]
            }
            values.append(1+len(wt['deps'])) # Initial guess
            meta[('wt', ticket, slot)] = wt
            running_index += 1

            wc = {
    #            'index': running_index,
                'deps': [('wt', ticket, slot)] + [('wt', t, s) for (t, s) in pairs if t == ticket and s != slot]
            }
    #        values.append(1.0/len(wc['deps']) if len(wc['deps']) > 0 else 1) # Initial guess
            meta[('wc', ticket, slot)] = wc
    #        running_index += 1
    '''
    for k, v in meta.iteritems():
        # print k, '-->', v
    # print values
    '''
    # assert len(values) == len(meta)
    # Modify the dependencies of the wt()s to include the dependencies of their wc()s
    for key, value in meta.iteritems():
        if key[0] == 'wt':
            meta[key]['deps'] = [ meta[wc]['deps'] for wc in value['deps'] ]
            # # print key, '-->', value['deps']
    # print '--------------------'
    # Replace the tuples in dependencies with the indicies of those tuples.
    wt_meta = {}
    for k, v in meta.iteritems():
        if k[0] != 'wt':
            continue
        # meta[k]['deps'] = [ meta[k2]['index'] for k2 in v['deps'] ]
        newval = {
            'index': v['index'],
            'deps': []
        }
        newval['deps'] = [ [meta[k2]['index'] for k2 in subdep] for subdep in v['deps'] ]
        wt_meta[k] = newval
        # # print k, '-->  index:', wt_meta[k]['index'], 'deps:', wt_meta[k]['deps']

    '''
    for k, v in meta.iteritems():
        # print k, '-->', v
    '''
    def optimized_computing_function(triple, entry):
        deps, myindex = entry['deps'], entry['index']
        def wt_func(values):
            return 1.0 + sum(
                                 1.0 / values[subdep[0]] / sum(
                                                                       1.0 / values[index]
                                                                       for index in subdep)
                                 for subdep in deps ) - values[myindex]
        return wt_func

    # random_key = random.sample(wt_meta.keys(), 1)[0]
    # # print 'random key:', random_key
    # # print optimized_computing_function(random_key, wt_meta[random_key])([1 for _ in values])
    # raise 'Done'

    def computing_function(triple, entry):    
        if triple[0] == 'wt':
            deps = entry['deps']
            myindex = entry['index']
            def wt_func(values):
                # return 1.0 + sum(map(lambda index : values[index], deps)) - values[myindex]
                return 1.0 + sum(values[index] for index in deps) - values[myindex]
            return wt_func
        elif triple[0] == 'wc':
            deps = entry['deps']
            myindex = entry['index']
            def wc_func(values):
                mypart = 1.0 / values[deps[0]]
                return mypart / (mypart + sum(1.0 / values[index] for index in deps[1:])) - values[myindex]
            return wc_func
        else:
            raise Exception("Found a triple whose type is neither 'wt' nor 'wc'")

    # # print computing_function(('wt', 'a', 1), meta[('wt', 'a', 1)])(values)

    # ordered_meta = sorted([(triple, entry) for triple, entry in meta.iteritems()], 
    #                                 key=lambda (k, v): v['index'])
    ordered_wt_meta = sorted([(triple, entry) for triple, entry in wt_meta.iteritems()], 
                                    key=lambda (k, v): v['index'])

    # iteration = 1
    def equations():
        # funcs = [computing_function(triple, entry) for (triple, entry) in ordered_meta]
        funcs = [optimized_computing_function(triple, entry) for (triple, entry) in ordered_wt_meta]
        def equations_inner(vals):
            # global iteration
            # # print 'iteration', iteration, '. vals:', vals
            # iteration += 1
            return [f(vals) for f in funcs]
        return equations_inner

    begin = time()
    #results = fsolve(equations(), [1 for _ in values])#, xtol=0.01)
    #results = fsolve(equations(), values, xtol=0.01)
    results = fsolve(equations(), values)
    # print 'That took', time()-begin, 'seconds.'
    # # print 'results:', results
    # for k, v in wt_meta.iteritems():
        # print k, '-->', results[v['index']]
    # print 'iterated', iteration, 'times'
for _ in range(1):    
    run_it()
