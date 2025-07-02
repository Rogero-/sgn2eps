import sys, re, struct

def parse_eps_coords(eps_path):
    coords = []
    with open(eps_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            cmd = parts[-1]
            if cmd in ("moveto","lineto"):
                x, y = float(parts[0]), float(parts[1])
                coords.append((int(x), int(y)))
            elif cmd == "curveto":
                vals = list(map(float, parts[:-1]))
                # group into (x1,y1),(x2,y2),(x3,y3)
                for i in range(0,6,2):
                    coords.append((int(vals[i]), int(vals[i+1])))
    return coords

def find_in_sgn(sgn_path, coords):
    data = open(sgn_path, "rb").read()
    hits = {}
    for x,y in set(coords):
        pat = struct.pack("<hh", x, y)
        idxs = [i for i in range(len(data))
                if data.startswith(pat, i)]
        if idxs:
            hits[(x,y)] = idxs
    return data, hits

def main():
    if len(sys.argv)!=3:
        print("Usage: python discover_format.py file.sgn file.eps")
        sys.exit(1)

    sgn, hits = find_in_sgn(sys.argv[1],
                             parse_eps_coords(sys.argv[2]))
    for (x,y), idxs in hits.items():
        print(f"Coord {(x,y)} → offsets {idxs}")
        for off in idxs[:5]:  # show up to 5 examples
            # opcode is the byte right before the coord bytes
            op = sgn[off-1]
            print(f"  opcode byte @ {off-1}: 0x{op:02X}")
    print("\nTotal unique coords found:", len(hits))

if __name__=="__main__":
    main()
