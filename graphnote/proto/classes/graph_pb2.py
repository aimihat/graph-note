# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: graph.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bgraph.proto\"!\n\x04Port\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\"4\n\nConnection\x12\x13\n\x04\x66rom\x18\x01 \x01(\x0b\x32\x05.Port\x12\x11\n\x02to\x18\x02 \x01(\x0b\x32\x05.Port\"t\n\x04\x43\x65ll\x12\x0b\n\x03uid\x18\x01 \x01(\t\x12\x0c\n\x04\x63ode\x18\x02 \x01(\t\x12\x17\n\x08in_ports\x18\x03 \x03(\x0b\x32\x05.Port\x12\x18\n\tout_ports\x18\x04 \x03(\x0b\x32\x05.Port\x12\x13\n\x06output\x18\x05 \x01(\tH\x00\x88\x01\x01\x42\t\n\x07_output\"T\n\x05Graph\x12\x13\n\x04root\x18\x01 \x01(\x0b\x32\x05.Cell\x12\x14\n\x05\x63\x65lls\x18\x02 \x03(\x0b\x32\x05.Cell\x12 \n\x0b\x63onnections\x18\x03 \x03(\x0b\x32\x0b.Connectionb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'graph_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _PORT._serialized_start=15
  _PORT._serialized_end=48
  _CONNECTION._serialized_start=50
  _CONNECTION._serialized_end=102
  _CELL._serialized_start=104
  _CELL._serialized_end=220
  _GRAPH._serialized_start=222
  _GRAPH._serialized_end=306
# @@protoc_insertion_point(module_scope)
