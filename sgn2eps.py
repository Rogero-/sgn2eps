#!/usr/bin/env python3
import sys, struct

# SGN opcodes
OP_MOVE  = 0x01
OP_LINE  = 0x02
OP_CURVE = 0x03
OP_END   = 0xFF

def parse_commands(blob):
    """
    Scan blob for [op][data…], return list of (opcode, ...) 
    """
    ptr = 0
    cmds = []
    while ptr < len(blob):
        op = blob[ptr]
        ptr += 1
        if op == OP_END:
            break

        if op in (OP_MOVE, OP_LINE):
            if ptr + 4 > len(blob): break
            x, y = struct.unpack_from("<hh", blob, ptr)
            ptr += 4
            cmds.append((op, x, y))

        elif op == OP_CURVE:
            if ptr + 12 > len(blob): break
            pts = struct.unpack_from("<hhhhhh", blob, ptr)
            ptr += 12
            cmds.append((op, *pts))

        else:
            # stop on first unknown and return what we have
            print(f"[WARN] Unknown opcode 0x{op:02X} at offset {ptr-1}")
            break

    return cmds

def find_best_offset(data):
    """
    Try every index where data[i] is a known op, parse from there,
    and pick the offset yielding the most commands.
    """
    best = (0, [])
    for i, b in enumerate(data):
        if b in (OP_MOVE, OP_LINE, OP_CURVE):
            cmds = parse_commands(data[i:])
            if len(cmds) > len(best[1]):
                best = (i, cmds)
    return best  # (best_offset, best_cmd_list)

def write_eps(path, cmds, canvas=(600,600)):
    w, h = canvas
    with open(path, "w") as f:
        f.write("%!PS-Adobe-3.0 EPSF-3.0\n")
        f.write(f"%%BoundingBox: 0 0 {w} {h}\nnewpath\n")

        for op, *pts in cmds:
            if op == OP_MOVE:
                x, y = pts
                f.write(f"{x} {y} moveto\n")
            elif op == OP_LINE:
                x, y = pts
                f.write(f"{x} {y} lineto\n")
            elif op == OP_CURVE:
                x1,y1,x2,y2,x3,y3 = pts
                f.write(f"{x1} {y1} {x2} {y2} {x3} {y3} curveto\n")

        f.write("stroke\nshowpage\n")

    print(f"[INFO] Wrote {len(cmds)} commands to EPS: {path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python sgn2eps.py input.sgn output.eps")
        sys.exit(1)

    data = open(sys.argv[1], "rb").read()
    offset, cmds = find_best_offset(data)

    print(f"[DEBUG] Best offset: {offset} (0x{offset:X}), commands found: {len(cmds)}")
    snippet = data[offset-8 : offset+16]
    print("[DEBUG] Bytes around offset:", 
          " ".join(f"{b:02X}" for b in snippet))

    # Show first few commands
    for i, c in enumerate(cmds[:10]):
        print(f"[CMD] #{i:02d} ->", c)

    write_eps(sys.argv[2], cmds)

if __name__ == "__main__":
    main()
