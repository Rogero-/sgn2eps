#!/usr/bin/env python3
import sys
import struct

# Candidate opcodes
OPCODES = {
    0x01: "M",   # MoveTo
    0x02: "L",   # LineTo
    0x03: "C",   # CurveTo
    0xFF: "END"  # End of data
}

def find_header_offset(data):
    """
    Scan data for the first byte matching any known opcode.
    Returns the index of that byte.
    """
    for i, b in enumerate(data):
        if b in OPCODES:
            return i
    return None

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
        if opcode == 0xFF:  # END
            break
        if opcode == 0x01 or opcode == 0x02:
            x, y = struct.unpack_from("<hh", blob, ptr)
            ptr += 4
            cmds.append((OPCODES[opcode], x, y))
        elif opcode == 0x03:
            pts = struct.unpack_from("<hhhhhh", blob, ptr)
            ptr += 12
            cmds.append((OPCODES[opcode],) + pts)
        else:
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
    data = open(sgn_path, "rb").read()

    offset = find_header_offset(data)
    if offset is None:
        print("[ERROR] No valid opcode found in file")
        sys.exit(1)

    print(f"[DEBUG] Detected first opcode {hex(data[offset])} at byte offset {offset}")
    # Dump surrounding bytes for verification
    start = max(0, offset - 8)
    snippet = data[start: start + 24]
    print("[DEBUG] Byte snippet around start:", " ".join(f"{b:02X}" for b in snippet))

    blob = data[offset:]
    cmds = parse_commands(blob)
    print(f"[DEBUG] Parsed {len(cmds)} commands")

    write_eps(eps_path, cmds)

if __name__ == "__main__":
    main()
