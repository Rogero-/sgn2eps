#!/usr/bin/env python3
import sys, struct

# Opcodes
OP_MOVE  = 0x01
OP_LINE  = 0x02
OP_CURVE = 0x03
OP_END   = 0xFF

def find_data_start(data):
    """Find first occurrence of 0x01/0x02/0x03."""
    for i, b in enumerate(data):
        if b in (OP_MOVE, OP_LINE, OP_CURVE):
            return i
    return None

def parse_commands(blob):
    """Yield (“M”/“L”/“C”, coords…) until OP_END."""
    ptr = 0
    cmds = []
    while ptr < len(blob):
        op = blob[ptr]
        ptr += 1
        if op == OP_END:
            break
        if op in (OP_MOVE, OP_LINE):
            x,y = struct.unpack_from("<hh", blob, ptr)
            ptr += 4
            cmds.append(("M" if op==OP_MOVE else "L", x, y))
        elif op == OP_CURVE:
            pts = struct.unpack_from("<hhhhhh", blob, ptr)
            ptr += 12
            cmds.append(("C",) + pts)
        else:
            print(f"[WARN] Unknown opcode 0x{op:02X} at offset {ptr-1}")
            break
    return cmds

def write_eps(fn, cmds, size=(600,600)):
    w,h = size
    with open(fn, "w") as f:
        f.write("%!PS-Adobe-3.0 EPSF-3.0\n")
        f.write(f"%%BoundingBox: 0 0 {w} {h}\nnewpath\n")
        for c in cmds:
            if c[0]=="M": f.write(f"{c[1]} {c[2]} moveto\n")
            if c[0]=="L": f.write(f"{c[1]} {c[2]} lineto\n")
            if c[0]=="C":
                f.write(f"{c[1]} {c[2]} {c[3]} {c[4]} {c[5]} {c[6]} curveto\n")
        f.write("stroke\nshowpage\n")
    print(f"[INFO] EPS written to {fn}")

def main():
    if len(sys.argv)!=3:
        print("Usage: python sgn2eps.py in.sgn out.eps")
        sys.exit(1)

    data = open(sys.argv[1],"rb").read()
    start = find_data_start(data)
    if start is None:
        print("[ERROR] No move/line/curve opcode found")
        sys.exit(1)

    print(f"[DEBUG] Data starts at byte offset {start} (0x{start:02X})")
    snippet = data[start-8:start+16]
    print("[DEBUG] Snippet around start:",
          " ".join(f"{b:02X}" for b in snippet))

    cmds = parse_commands(data[start:])
    print(f"[DEBUG] Parsed {len(cmds)} commands")
    write_eps(sys.argv[2], cmds)

if __name__=="__main__":
    main()
