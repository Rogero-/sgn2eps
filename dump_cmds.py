#!/usr/bin/env python3
import struct

# tweak this if your header size changes
HEADER_SIZE = 70  

data = open("adidas.sgn","rb").read()[HEADER_SIZE:]
ptr = 0
cmds = []

while ptr < len(data):
    op = data[ptr]
    ptr += 1
    if op == 0xFF:
        break
    if op in (1,2):          # MOVETO or LINETO
        if ptr+4 > len(data): break
        x,y = struct.unpack_from("<hh", data, ptr)
        ptr += 4
        cmds.append((op, x, y))
    elif op == 3:            # CURVETO
        if ptr+12 > len(data): break
        pts = struct.unpack_from("<hhhhhh", data, ptr)
        ptr += 12
        cmds.append((op,)+pts)
    else:
        break

# collect only the first two coords of each op for min/max
xs = [c[1] for c in cmds if c[0] in (1,2)]
ys = [c[2] for c in cmds if c[0] in (1,2)]

print(f"Total commands parsed: {len(cmds)}")
print(f"X range: {min(xs)} … {max(xs)}")
print(f"Y range: {min(ys)} … {max(ys)}\n")

print("First 10 commands:")
for c in cmds[:10]:
    print(" ", c)
