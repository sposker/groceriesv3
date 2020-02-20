with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\new_store.yaml') as f:
    lines = sorted(line for line in f)

with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\new_store.yaml', 'w') as f:
    f.write(''.join(lines))
