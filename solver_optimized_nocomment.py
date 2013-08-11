
import random
from scipy.optimize import fsolve
from time import time
def run_it():
    ntickets = 20
    nslots = 25
    random_input = [ random.sample(['t%d' % i for i in range(1, ntickets+1)], random.randint(0, ntickets)) for _ in range(nslots) ]
    real_input = random_input
    pairs = [(t, s) for s, queue in enumerate(real_input) for t in queue if len(t) > 0]

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
                'deps': [('wt', ticket, slot)] + [('wt', t, s) for (t, s) in pairs if t == ticket and s != slot]
            }
            meta[('wc', ticket, slot)] = wc
    for key, value in meta.iteritems():
        if key[0] == 'wt':
            meta[key]['deps'] = [ meta[wc]['deps'] for wc in value['deps'] ]
    wt_meta = {}
    for k, v in meta.iteritems():
        if k[0] != 'wt':
            continue
        newval = {
            'index': v['index'],
            'deps': []
        }
        newval['deps'] = [ [meta[k2]['index'] for k2 in subdep] for subdep in v['deps'] ]
        wt_meta[k] = newval

    def optimized_computing_function(triple, entry):
        deps, myindex = entry['deps'], entry['index']
        def wt_func(values):
            return 1.0 + sum(
                                 1.0 / values[subdep[0]] / sum(
                                                                       1.0 / values[index]
                                                                       for index in subdep)
                                 for subdep in deps ) - values[myindex]
        return wt_func


    def computing_function(triple, entry):    
        if triple[0] == 'wt':
            deps = entry['deps']
            myindex = entry['index']
            def wt_func(values):
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


    ordered_wt_meta = sorted([(triple, entry) for triple, entry in wt_meta.iteritems()], 
                                    key=lambda (k, v): v['index'])

    def equations():
        funcs = [optimized_computing_function(triple, entry) for (triple, entry) in ordered_wt_meta]
        def equations_inner(vals):
            return [f(vals) for f in funcs]
        return equations_inner

    begin = time()
    results = fsolve(equations(), values)
for _ in range(1):    
    run_it()
