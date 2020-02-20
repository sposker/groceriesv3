with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\username\username0.yaml', 'w') as output:
    with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\username\username.yaml') as f:
        for line in f:
            if 'uid:' in line:
                start, end = line.rsplit('i', maxsplit=1)
                line = 'i'.join([start, str(int(end)).zfill(3) + '\n'])
            output.write(line)
