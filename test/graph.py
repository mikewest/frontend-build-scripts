#!/usr/bin/env python
# encoding: utf-8;

import unittest
import os, sys

TESTROOT = os.path.dirname( os.path.abspath( __file__ ) )
libpath = [ os.path.join( TESTROOT, "..", "src" ) ]
libpath.extend( sys.path )
sys.path = libpath
from graph import Node, DAG, DuplicateInsertionError, CyclicInsertionError, NodeNotExists

class MockNode(Node):
    def id(self):
        return self._id
    def setId(self, id):
        self._id = id


class TestDAG(unittest.TestCase):
    def setUp(self):
        self.graph = DAG()

    def test_insertion(self):
        self.assertEqual( len(self.graph.nodes()), 0 )
        self.graph.addNode(MockNode('id1'))
        self.assertTrue( self.graph.contains( 'id1' ) )
        self.assertRaises(DuplicateInsertionError, lambda: self.graph.addNode(MockNode('id1')))

    def test_edgeinsertion(self):
        self.graph.addNode(MockNode('id1'))
        self.graph.addNode(MockNode('id2'))
        self.assertRaises(NodeNotExists, lambda: self.graph.addEdge('id1', 'id3'))
        self.assertRaises(NodeNotExists, lambda: self.graph.addEdge('id3', 'id1'))

        self.graph.addEdge('id1', 'id2')
        self.assertEquals(self.graph.neighbors('id1'), [ 'id2' ])
        self.assertEquals(self.graph.neighbors('id2'), [])

    def test_cycledetection_simple(self):
        self.graph.addNode(MockNode('id1'))
        self.graph.addNode(MockNode('id2'))
        self.graph.addEdge('id1','id2')
        self.assertRaises(CyclicInsertionError, lambda: self.graph.addEdge('id2','id1'))
    
    def test_cycledetection_complex(self):
        prev = None
        for x in range( 100 ):
            self.graph.addNode(MockNode(x))
            if prev is not None:
                self.graph.addEdge(prev, x)
            prev = x
        self.assertRaises(CyclicInsertionError, self.graph.addEdge(99, 0))


if __name__ == '__main__':
    unittest.main()
