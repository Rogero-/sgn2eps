data = open("adidas.sgn","rb").read()
print("SGN header (first 64 bytes):")
print(" ".join(f"{b:02X}" for b in data[:64]))
