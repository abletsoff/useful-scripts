#!/usr/bin/python3

import json, sys, csv

rows = []

for filename in sys.argv[1:]:
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # skip bad lines

            addr = data.get("addr", "")
            for port in data.get("ports", []):
                portnum = port.get("port")
                if not portnum or portnum < 1:
                    continue

                name = port.get("service_name", "").strip()
                product = port.get("service_product", "").strip()

                if name and product:
                    service = f"{name}: {product}"
                else:
                    service = name or product

                rows.append([addr, f"{port.get('protocol','')}/{portnum}", service])

writer = csv.writer(sys.stdout)
writer.writerow(["addr","port","service"])
writer.writerows(rows)
