import jne
import json
import sys

if len(sys.argv) != 2:
    print(f"Usage: python3 {sys.argv[0]} <resi>")
    raise SystemExit

resi = sys.argv[1]
info_resi = jne.cek_resi(resi)
print(info_resi)