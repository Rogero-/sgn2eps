import sys, re, struct

# match only moveto/lineto/curveto lines
RE_MOVE  = re.compile(r'^\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+moveto')
RE_LINE  = re.compile(r'^\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+lineto')
RE_CURVE = re.compile(
    r'^\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
    r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+'
    r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+curveto'
)

def parse_eps_coords(eps_path):
    coords = []
    with open(eps_path, 'r') as f:
        for line in f:
            m = RE_MOVE.match(line) or RE_LINE.match(line)
            if m:
                x,y = map(float, m.groups())
                coords.append((int(round(x)), int(round(y))))
                continue
            m = RE_CURVE.match(line)
            if m:
                vals = list(map(float, m.groups()))
                for i in range(0,6,2):
                    coords.append((int(round(vals[i])), int(round(vals[i+1]))))
    return coords

def find_in_sgn(sgn_path, coords):
    data = open(sgn_path, 'rb').read()
    hits = {}
    for x,y in set(coords):
        pat = struct.pack('<hh', x, y)
        idxs = [i for i in range(len(data)) if data.startswith(pat, i)]
        if idxs:
            hits[(x,y)] = idxs
    return data, hits

def main():
    if len(sys.argv)!=3:
        print("Usage: python discover_format.py file.sgn file.eps")
        sys.exit(1)

    sgn_path, eps_path = sys.argv[1], sys.argv[2]
    coords = parse_eps_coords(eps_path)
    print(f"EPS coords found: {len(coords)} total, {len(set(coords))} unique\n")

    data, hits = find_in_sgn(sgn_path, coords)
    if not hits:
        print("No matches—check your EPS syntax or rounding.")
        return

    for (x,y), idxs in hits.items():
        print(f"Coord {(x,y)} → SGN offsets: {idxs[:5]}")
        for off in idxs[:5]:
            opcode = data[off-1]
            print(f"  byte @ {off-1}: 0x{opcode:02X}")
    print(f"\nTotal coords mapped: {len(hits)}")

if __name__=='__main__':
    main()
