import os
import sys


def push(destination, options=None):
    global exclude

    images = False

    if options:
        for i in options:
            exclude.remove(i.replace('--', ''))
            print(i.replace('--', ''))

        if 'src' not in exclude:
            images = True
            exclude.add('src')

    for root, dirs, files in os.walk(base, topdown=True):
        [dirs.remove(d) for d in list(dirs) if d in exclude]
        new_root = root.replace(base, destination)
        for file in files:

            with open(os.path.join(root, file)) as f:
                text = ''.join(f.readlines())
            try:
                f = open(os.path.join(new_root, file), 'w', encoding='utf-8')
            except FileNotFoundError:
                os.makedirs(new_root)
                f = open(os.path.join(new_root, file), 'w', encoding='utf-8')
            finally:
                f.write(text)
                f.close()

    if images:
        from PIL import Image

        try:
            os.makedirs(os.path.join(destination, 'src'))
        except FileExistsError:
            pass

        for root, _, files in os.walk(os.path.join(base, 'src')):
            new_root = root.replace(base, destination)
            for f in files:
                im = Image.open(os.path.join(root, f))
                im.save(os.path.join(new_root, f))


mint = {_m: r'C:\Users\Oliver\documents\mint\g2' for _m in {'--mint', '-m'}}
len_pc = {_l: r'\\LEN-PC\Users\Public\Documents\groceriesv2' for _l in {'--lenpc', '-l'}}

base = r'C:\Users\Oliver\PycharmProjects\groceriesv2'
mapping = {}
mapping.update(mint)
mapping.update(len_pc)
mapping['-ml'] = tuple(set(mapping.values()))
mapping['-lm'] = tuple(set(mapping.values()))

exclude = {'.git', '.idea', '__pycache__', 'venv', 'data', 'access', '_demos', '_kivymd'}

try:
    my_flags = mapping[sys.argv[1]]
except IndexError:
    print('Run from terminal and choose a destination')
    exit()
except KeyError:
    print('Invalid argument [0]')
    exit()

options = sys.argv[2:].copy()
print(options)

if isinstance(my_flags, tuple):
    for loc in my_flags:
        if options:
            push(loc, options=options)
        else:
            push(loc)
else:
    if options:
        push(my_flags, options=options)
    else:
        push(my_flags)