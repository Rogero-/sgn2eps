#!/usr/bin/env python3
import sys
import struct

# SGN format constants (tweak if needed)
HEADER_SIZE = 32
OP_MOVE   = 0x01
OP_LINE   = 0x02
OP_CURVE  = 0x03
OP_END    = 0xFF

def read_sgn(path):
    data = open(path, "rb").read()
    if len(data) <= HEADER_SIZE:
        raise ValueError("File too small or wrong HEADER_SIZE")
    return data[HEADER_SIZE:]

def parse_commands(blob):
    """
    Yields drawing commands as tuples:
      ("M", x, y)
      ("L", x, y)
      ("C", x1, y1, x2, y2, x3, y3)
    """
    ptr = 0
    cmds = []
    while ptr < len(blob):
        opcode = blob[ptr]
        ptr += 1
        if opcode == OP_END:
            break
        elif opcode in (OP_MOVE, OP_LINE):
            # 2 bytes X, 2 bytes Y
            x, y = struct.unpack_from("<hh", blob, ptr)
            ptr += 4
            cmds.append(("M" if opcode == OP_MOVE else "L", x, y))
        elif opcode == OP_CURVE:
            pts = struct.unpack_from("<hhhhhh", blob, ptr)
            ptr += 12
            cmds.append(("C",) + pts)
        else:
            # Unknown opcode: stop or skip
            print(f"[WARN] Unknown opcode 0x{opcode:02X} at {ptr-1}")
            break
    return cmds

def write_eps(path, cmds, canvas_size=(600,600)):
    w, h = canvas_size
    with open(path, "w") as f:
        f.write("%!PS-Adobe-3.0 EPSF-3.0\n")
        f.write(f"%%BoundingBox: 0 0 {w} {h}\n")
        f.write("newpath\n")
        for cmd in cmds:
            if cmd[0] == "M":
                _, x, y = cmd
                f.write(f"{x} {y} moveto\n")
            elif cmd[0] == "L":
                _, x, y = cmd
                f.write(f"{x} {y} lineto\n")
            elif cmd[0] == "C":
                _, x1, y1, x2, y2, x3, y3 = cmd
                f.write(f"{x1} {y1} {x2} {y2} {x3} {y3} curveto\n")
        f.write("stroke\nshowpage\n")
    print(f"[INFO] Written EPS to {path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python sgn2eps.py input.sgn output.eps")
        sys.exit(1)

    sgn_path, eps_path = sys.argv[1], sys.argv[2]
    raw_blob = read_sgn(sgn_path)
    cmds = parse_commands(raw_blob)
    print(f"[DEBUG] Parsed {len(cmds)} commands")
    write_eps(eps_path, cmds)

if __name__ == "__main__":
    main()
