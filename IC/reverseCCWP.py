from __future__ import division
from copy import deepcopy
import time, random, operator
from heapq import nlargest
from IC import avgSize
import networkx as nx

def reverseCCWP(G, tsize, p, R, iterations):
    '''
     Input:
     G -- undirected graph (nx.Graph)
     tsize -- coverage size (int)
     p -- propagation probability among all edges (int)
     R -- number of iterations to discover CCs (int)
     iterations -- number of iterations to run IC to calculate influence spread
     Output:
     S -- seed set
    '''
    scores = dict(zip(G.nodes(), [0]*len(G))) # initialize scores
    start = time.time()
    minL = float("Inf") # number of nodes we start with (tbd later)
    maxL = 1
    for it in range(R):
        # remove blocked edges from graph G
        E = deepcopy(G)
        edge_rem = [e for e in E.edges() if random.random() < (1-p)**(E[e[0]][e[1]]['weight'])]
        E.remove_edges_from(edge_rem)

        # initialize CC
        CC = dict() # each component is reflection os the number of a component to its members
        explored = dict(zip(E.nodes(), [False]*len(E)))
        c = 0
        # perform BFS to discover CC
        for node in E:
            if not explored[node]:
                c += 1
                explored[node] = True
                CC[c] = [node]
                component = E[node].keys()
                for neighbor in component:
                    if not explored[neighbor]:
                        explored[neighbor] = True
                        CC[c].append(neighbor)
                        component.extend(E[neighbor].keys())

        # find top components that can reach tsize activated nodes
        sortedCC = sorted([(len(dv), dk) for (dk, dv) in CC.iteritems()], reverse=True)
        cumsum = 0 # sum of top components
        curL = 0 # current number of CC that achieve tsize
        # find curL first
        for length, numberCC in sortedCC:
            curL += 1
            cumsum += length
            if cumsum >= tsize:
                break
        print curL, cumsum
        # assign scores to L components
        for length, numberCC in sortedCC[:curL]:
            weighted_score = 1.0/(length*curL)
            for node in CC[numberCC]:
                scores[node] += weighted_score
        if curL < minL:
            minL = curL
        if curL > maxL:
            maxL = curL

        print it + 1, R, time.time() - start
    print 'maxL', maxL
    print 'minL', minL
    # find nodes that achieve tsize coverage starting from top-minL scores nodes
    orderedScores = sorted(scores.iteritems(), key = operator.itemgetter(1), reverse=True)
    topScores = orderedScores[:maxL]
    S = [node for (node,_) in topScores]
    coverage = avgSize(G, S, p, iterations)
    print 'Top %s nodes achieved coverage: %s out of %s necessary' %(maxL, coverage, tsize)
    extra = 0
    while coverage < tsize:
        new_node, _ = orderedScores[maxL + extra]
        S.append(new_node)
        extra += 1
        coverage = avgSize(G, S, p, iterations)
        print '|S| = %s --> %s' %(len(S), coverage)
    return S

if __name__ == '__main__':
    import time
    start = time.time()

    # read in graph
    G = nx.Graph()
    with open('../graphdata/hep.txt') as f:
        n, m = f.readline().split()
        for line in f:
            u, v = map(int, line.split())
            try:
                G[u][v]['weight'] += 1
            except:
                G.add_edge(u, v, weight=1)
    print 'Built graph G'
    print time.time() - start

    tsize = 150
    p = .01
    R = 2000
    iterations = 1000
    S = reverseCCWP(G, tsize, p, R, iterations)
    print S
    print 'Necessary %s initial nodes to target %s nodes in graph G' %(len(S), tsize)
    print time.time() - start
    console = []