#!/usr/bin/env python

from smart.triplestore import TripleStore 
from smart.models.record_object import api_types, Record, RecordObject
from smart.client.common.util import parse_rdf, serialize_rdf, remap_node, bound_graph, URIRef, Literal, BNode, sp, rdf
from django.conf import settings
import sys

"""
To run:

PYTHONPATH=/path/to/smart_server \
  DJANGO_SETTINGS_MODULE=settings \
  /usr/bin/python \
  load_tools/load_one_patient.py \
  records/* 
"""
class RecordImporter(object):
    def __init__(self, filename, target_id=None):            
        # 0. Read supplied data
        self.target_id = target_id
        self.data = parse_rdf(open(filename).read())

        # 1. For each known data type, extract relevant nodes
        var_bindings = {'record_id': self.target_id}
        self.ro = RecordObject[sp.Statement]    
        self.ro.prepare_graph(self.data, None, var_bindings)
        print "Default context", len(self.data.default_context)
        
        record_node = list(self.data.triples((None, rdf.type, sp.MedicalRecord)))
        assert len(record_node) == 1, "Found statements about >1 patient in file: %s" % record_node
        record_node = record_node[0][0]
        self.record_node = record_node
        self.segregate_nodes(record_node, record_node)
        self.data.remove_context(self.data.default_context)

        # 2. Copy extracted nodes to permanent RDF store
        self.write_to_record()
        print self.data.default_context.identifier.n3()
            
    def segregate_nodes(self, r, context):

        # Recursion base case:  we've already started evaluating
        # this node as a root before --> don't evaluate it again!
        if r==context and len(self.data.get_context(context)) >0:
            return

        nodes_to_recurse = {}
        for s,p,o in self.data.triples((r, None, None)):
            self.data.get_context(context).add((s,p,o))
            
            if type(o) == Literal:
                continue

            nodes_to_recurse[o] = o
            if not self.ro.statement_type(self.data, o):
                nodes_to_recurse[o] = context
           
        for node, context in nodes_to_recurse.iteritems():
            self.segregate_nodes(node, context)

        return

    def write_to_record(self):
            rconn =TripleStore()
            rconn.transaction_begin() 
            r, created = Record.objects.get_or_create(id=self.target_id)
            print "Wiping record", self.record_node.n3()
            rconn.destroy_context_and_neighbors(self.record_node)

            # TODO:  clear any elements in this record that may still exist
            rconn.replace_conjunctive_graph(self.data)

            print "adds: ",len(self.data)
            rconn.transaction_commit() 

if __name__ == "__main__":
    import string
    for v in sys.argv[1:]:
        rid = filter(str.isdigit, v.split("/")[-1].split(".")[0])
        print "Using record id: %s"%rid
        RecordImporter(v, rid)
