#!/usr/bin/env python
# encoding: utf-8;

import logging
from sys import getrecursionlimit, setrecursionlimit

class Node(object):
    def __init__(self, id):
        self.setId(id)

    def id(self):
        raise NotImplementedError( "`id` method ought be implemented." )

    def setId(self, id):
        raise NotImplementedError( "`setId` method ought be implemented." )

class DuplicateInsertionError(RuntimeError):
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return "Node `%s` is already in the graph: it can't be inserted twice." % node.id()

class CyclicInsertionError(RuntimeError):
    def __init__(self, cycle):
        self.cycle = cycle
    def __str__(self):
        return "Graph contains a cycle: `%s`" % " --> ".join( self.cycle )

class NodeNotExists(RuntimeError):
    pass

class DAG(object):
    def __init__(self):
        self._nodes = {}
        self._edges = {}

    def nodes(self):
        return self._nodes

    def contains(self, id):
        return self._nodes.has_key(id)

    def neighbors(self, id):
        if self.contains(id):
            return self._edges[id].keys()
        else:
            raise NodeNotExists(id)

    def addNode(self, node):
        """
            Adds a node to the DAG.  Returns the node on success, or raises a
            runtime error.
        """
        logging.debug("Adding node `%s`" % node.id())
        if self.contains(node.id()):
            raise DuplicateInsertionError( node )

        self._nodes[node.id()] = node
        self._edges[node.id()] = {}
        return node

    def addNodes(self, nodes):
        for n in nodes:
            self.add_node(n)

    def addEdge(self, fromId, toId):
        logging.debug("Adding edge from `%s` to `%s`" % ( fromId, toId ) )
        if self.contains( fromId ) and self.contains( toId ):
            self._edges[fromId][toId]   = True
            is_cyclic = self.detectCycles( fromId, toId )
            if is_cyclic:
                raise CyclicInsertionError(is_cyclic)
        else:
            raise NodeNotExists( toId if self.contains( fromId ) else fromId )
                

    def addEdgesFromNode(self, fromId, toIds):
        for to in toIds:
            self.addEdge(fromId, to)

    def detectCycles(self, fromId, toId):
        """Detect cycles arising from an addition of an edge from `fromId` to `toId`"""
        
        def dfs(needle, root, path):
            logging.debug( "DFS: `%s`, `%s`, `%s`" % ( needle, root, path ) )
            for edgeId in self._edges[root].keys():
                newpath = path
                newpath.append( root )
                if needle == edgeId:
                    newpath.append( edgeId )
                    return newpath
                else:
                    newpath = dfs( needle, edgeId, newpath )
                    if newpath:
                        return newpath
                
            return []

        return dfs( fromId, toId, [ fromId ] )
