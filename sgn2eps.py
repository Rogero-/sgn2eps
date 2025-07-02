#!/usr/bin/env python3
import sys, struct

# Opcodes
OP_MOVE, OP_LINE, OP_CURVE, OP_END = 0x01, 0x02, 0x03, 0xFF

# SGN coord range (your BB is 0..591 × 0..392)
X_MIN, X_MAX = 0, 591
Y_MIN, Y_MAX = 0, 392

def find_data_start(data):
    """
    Find the first OP_MOVE (0x01) whose following <hh> pair 
    falls inside [X_MIN..X_MAX]×[Y_MIN..Y_MAX].
    """
    for i in range(len(data) - 5):
        if data[i] == OP_MOVE:
            x, y = struct.unpack_from("<hh", data, i+1)
            if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
                return i
    return None

def parse_commands(blob):
    """Parse until OP_END, return list of (opcode, *pts)."""
    ptr, cmds = 0, []
    while ptr < len(blob):
        op = blob[ptr]
        ptr += 1
        if op == OP_END:
            break
        if op in (OP_MOVE, OP_LINE):
            if ptr+4 > len(blob): break
            x,y = struct.unpack_from("<hh", blob, ptr)
            ptr += 4
            cmds.append((op, x, y))
        elif op==OP_CURVE:
            if ptr+12 > len(blob): break
            pts = struct.unpack_from("<hhhhhh", blob, ptr)
            ptr += 12
            cmds.append((op, *pts))
        else:
            break
    return cmds

def write_eps(path, cmds, size=(591,392)):
    w,h = size
    with open(path, "w") as f:
        f.write("%!PS-Adobe-3.0 EPSF-3.0\n")
        f.write(f"%%BoundingBox: 0 0 {w} {h}\nnewpath\n")
        for op, *pts in cmds:
            if op==OP_MOVE:
                f.write(f"{pts[0]} {pts[1]} moveto\n")
            elif op==OP_LINE:
                f.write(f"{pts[0]} {pts[1]} lineto\n")
            else:
                x1,y1,x2,y2,x3,y3 = pts
                f.write(f"{x1} {y1} {x2} {y2} {x3} {y3} curveto\n")
        f.write("stroke\nshowpage\n")
    print(f"[INFO] Wrote {len(cmds)} ops to EPS: {path}")

def main():
    if len(sys.argv)!=3:
        print("Usage: python sgn2eps.py in.sgn out.eps")
        sys.exit(1)

    data = open(sys.argv[1],"rb").read()
    start = find_data_start(data)
    if start is None:
        print("[ERROR] Couldn’t find a valid moveto in-range.")
        sys.exit(1)

    print(f"[DEBUG] Data starts at offset {start} (0x{start:X})")
    snippet = data[start-8:start+16]
    print("[DEBUG] Bytes around:", " ".join(f"{b:02X}" for b in snippet))

    cmds = parse_commands(data[start:])
    for i,c in enumerate(cmds[:10]):
        print(f"[CMD] {i:2d} →", c)
    print(f"[DEBUG] Parsed total {len(cmds)} commands")

    write_eps(sys.argv[2], cmds)

if __name__=="__main__":
    main()
