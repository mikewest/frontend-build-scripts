#!/usr/bin/env python
# encoding: utf-8;

from __future__ import with_statement

import os
import errno
import sys
import re
import subprocess
import hashlib
import shutil
import logging
from graph import Node, DAG
from optparse import OptionParser

class Module(Node):
    def __init__(self, filename, package, module, requires ):
        super(Module,self).__init__(module)
        self._reqs      = set(requires)
        self._packages  = set(package)
        self._filename  = set(filename)

    def id(self):
        return self._id

    def setId(self, id):
        self._id = id

    def requirements(self):
        return self._reqs

class DependencyResolver(object):
    def __init__(self, path, options):
        logging.debug("Creating DependencyResolver")
        self.graph  = DAG()
        self.root   = path
        self.opts   = options

    def scan(self):
        for root, dirs, files in os.walk(self.root):
            for name in files:
                (base, ext) = os.path.splitext(name)
                if ext in ['.css', '.js']:
                    data = self.scanfile(os.path.join(root, name))
                    for module in data[ 'module' ]:
                        self.graph.addNode(
                            Module(
                                module=module,
                                filename=data['filename'],
                                package=data['package'],
                                requires=data['requires']
                            )
                        )
        for module in self.graph.nodes():
            self.graph.addEdgesFromNode(module.id(), module.requirements())

        

    def scanfile(self, path):
        logging.debug( "Scanning file: %s" % path )
        metadata    = {
            "filename": path,
            "package":  [],
            "module":   [],
            "requires": []
        }

        with open( path, 'r' ) as f:
            in_comment  = False
            for line in f:
                if in_comment:
                    if re.search( "\*\/", line ):
                        in_comment = False
                    else:
                        tags = re.search( "@(?P<name>\w+)\s+(?P<value>.+)\s*$", line )
                        if tags:
                            (name, value) = (tags.group( 'name' ), re.split( '\s*,\s*', tags.group( 'value' )))
                            if metadata.has_key( name ):
                                metadata[ name ].extend(value)
                else:
                    if re.match( "\s*\/\*\*", line ):
                        in_comment = True
        logging.debug( "   - Result: %s" % metadata )
        return metadata

def main(argv=None):
    if argv is None:
        argv = sys.argv

    default_root = os.path.dirname(os.path.abspath(__file__))

    parser = OptionParser(usage="Usage: %prog [options]", version="%prog 0.1")
    parser.add_option(  "--verbose",
                        action="store_true", dest="verbose_mode", default=False,
                        help="Verbose mode")
    
    parser.add_option(  "-o", "--output",
                        action="store",
                        dest="output_root", 
                        default=os.path.join(default_root, '../build'),
                        help="Directory to which output will be written")

    parser.add_option(  "-s", "--source",
                        action="store",
                        dest="source_root",
                        default=os.path.join(default_root, "../src"),
                        help="Directory from which source files will be read")
    
    parser.add_option(  "-c", "--compress",
                        action="store_true",
                        dest="compress",
                        default=False,
                        help="Compress the generated files using the specified compression command")

    parser.add_option(  "--cdn",
                        action="store_true",
                        dest="use_cdn",
                        default=False,
                        help="Generate CDN URLs for static assets in generated files.")
    (options, args) = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    deps = DependencyResolver( path=options.source_root, options=options )
    deps.scan()

if __name__ == "__main__":
    sys.exit(main())

