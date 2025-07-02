#!/usr/bin/env python3
import struct

# SGN opcodes
OP_MOVE, OP_LINE, OP_CURVE, OP_END = 0x01, 0x02, 0x03, 0xFF

# Your art’s bounding box
X_MIN, X_MAX =   0,  591
Y_MIN, Y_MAX =   0,  392

def is_valid_pt(x, y):
    return X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX

def count_run(data, offset, endian):
    """Count how many successive commands parse validly at offset."""
    ptr = offset
    run = 0
    while ptr < len(data):
        op = data[ptr]
        # end-of-stream
        if op == OP_END:
            break
        # move or line
        if op in (OP_MOVE, OP_LINE):
            if ptr+5 > len(data): break
            x,y = struct.unpack_from(endian+"hh", data, ptr+1)
            if not is_valid_pt(x,y): break
            ptr += 1 + 4
            run += 1
            continue
        # curve
        if op == OP_CURVE:
            if ptr+13 > len(data): break
            pts = struct.unpack_from(endian+"hhhhhh", data, ptr+1)
            # require at least the end‐point valid
            if not is_valid_pt(pts[4], pts[5]): break
            ptr += 1 + 12
            run += 1
            continue
        # unknown opcode
        break
    return run

def main():
    data = open("adidas.sgn","rb").read()
    candidates = []
    for i in range(0, len(data)-1):
        for endian in ("<", ">"):
            r = count_run(data, i, endian)
            if r >= 5:  # at least 5 valid commands in a row
                candidates.append((i, endian, r))
    # sort by longest run, then lowest offset
    candidates.sort(key=lambda x: (-x[2], x[0]))
    print("Top candidates for vector stream start:")
    for off, endian, run in candidates[:10]:
        print(f"  offset={off} (0x{off:X}), endian={endian!r}, run={run}")
    if not candidates:
        print("No runs ≥5 commands found; maybe loosen the threshold or range.")
    
if __name__=="__main__":
    main()
