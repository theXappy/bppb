import itertools
import struct
import sys
import wrapper_pb2


FORMAT_MAP = {1: 'B', 2: '?H', 4: '>I', 8: '>Q'}

def bytes_count_to_format(count):
    return FORMAT_MAP[count]

def calc_protobuf_header(blob_size):
    my_message = wrapper_pb2.Wrapper()
    my_message.Payload = b'\x00' * blob_size
    new_protobuf = my_message.SerializeToString()
    return len(new_protobuf) - blob_size

def merge(bplist, protobuf):
    # Parse bplist trailer
    trailer = struct.unpack(">bbqqq",bplist[-26:])
    offset_size = trailer[0]
    num_objects = trailer[2]
    offsets_table_pos = trailer[4]
    
    # Parse bplist offsets table
    offsets_table_data = bplist[offsets_table_pos:]
    offsets_format = bytes_count_to_format(offset_size)
    offsets_table = {}
    for i in range(0, num_objects):
        offset_pos = i * offset_size
        offset_data = offsets_table_data[offset_pos:offset_pos + offset_size]
        offsets_table[i], = struct.unpack(offsets_format, offset_data)

    hole_offset = 114
    hole_extension = 0
    objs_to_relocate = {k:v for (k,v) in offsets_table.items() if v >= hole_offset}
    objs_to_keep = {k:v for (k,v) in offsets_table.items() if v < hole_offset}

    if hole_offset not in objs_to_relocate.values() and objs_to_keep:
        # An object will be cut in half by the hole. Move it from 'keep' to 'relocate'
        max_key_before_hole = max(objs_to_keep, key=lambda k: objs_to_keep[k])
        max_offset_before_hole = objs_to_keep.pop(max_key_before_hole)
        objs_to_relocate[max_key_before_hole] = max_offset_before_hole
        # We'll need to compensate for those extra borrowed bytes
        hole_extension = hole_offset - max_offset_before_hole

    # Calculating how much data will be present AFTER the hole
    min_relocated_key = min(objs_to_relocate, key=lambda k: objs_to_relocate[k])
    min_relocated_offset = objs_to_relocate[min_relocated_key]
    data_size_after_hole = len(bplist) - min_relocated_offset
    hole_size = len(protobuf) + calc_protobuf_header(len(protobuf)) + calc_protobuf_header(data_size_after_hole)

    # Encode new offsets table
    relocate_shift = hole_size + hole_extension
    new_offsets_table = b''
    for i in range(num_objects):
        if i in objs_to_keep:
            new_offset = objs_to_keep[i]
        elif i in objs_to_relocate:
            new_offset = objs_to_relocate[i] + relocate_shift
        else:
            raise Exception(f"Load object with id = {i}")
        new_offsets_table += struct.pack(offsets_format, new_offset)

    # Combine all parts into a new bplist
    new_bplist = bplist[:hole_offset - hole_extension]
    new_bplist += b'\x00' * hole_extension

    # Instead of concatinaing the shifted data of the bplist straight into new_bplist,
    # we first encode it into and the payload protobuf together, to create the 2nd part of the file.
    footer = bplist[hole_offset - hole_extension : offsets_table_pos]
    new_offsets_table_pos = len(new_bplist) + hole_size + len(footer)
    footer += new_offsets_table
    # Copy most of the old trailer, but reaplce the offsets table position
    footer += bplist[-32:-8]
    footer += struct.pack(">Q", new_offsets_table_pos)

    # Compile the Payload and Footer element of the wrapper protobuf.
    my_message = wrapper_pb2.Wrapper()
    my_message.Payload = protobuf
    my_message.FooterPadding = footer
    new_protobuf = my_message.SerializeToString()
    assert(len(new_protobuf) == hole_size + len(footer))

    # Final concatinationg:
    # bplsit view: [Magic + some objects + hole extension filled] + ["hole" + some fields + offsets table + trailer]
    # protobuf view: [ID 12 LengthValue (HeaderPadding)] + [ID 1 LengthValue (Payload) + ID 2 LengthValue (FooterPadding)]
    new_bplist += new_protobuf

    return new_bplist

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} <bplist path> <protobuf path> <output path>")
        sys.exit(1)

    bplist_path = sys.argv[1]
    protobuf_path = sys.argv[2]
    output_path = sys.argv[3]

    bplist_data = open(bplist_path, "rb").read()
    protobuf_data = open(protobuf_path, "rb").read()
    new_bplist_data = merge(bplist_data, protobuf_data)
    fd = open(output_path, "wb")
    fd.write(new_bplist_data)
    fd.close()
    print(f"Results written to {output_path}")
