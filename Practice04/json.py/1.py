import json

with open("sample-data.json") as f:
    data = json.load(f)

print("Interface Status")
print("=" * 80)
print("DN".ljust(55), "Description".ljust(20), "Speed".ljust(8), "MTU")
print("-" * 80)

for item in data["imdata"]:
    attr = item["l1PhysIf"]["attributes"]
    dn = attr["dn"]
    descr = attr["descr"]
    speed = attr["speed"]
    mtu = attr["mtu"]

    print(dn.ljust(55), descr.ljust(20), speed.ljust(8), mtu)