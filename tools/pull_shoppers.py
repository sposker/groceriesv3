# import yaml
#
# data = {}
#
# with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\shoppers.yaml', 'w') as output:
#     with open('shoppers locs.yaml') as f:
#         for entries_list in yaml.load_all(f, Loader=yaml.Loader):
#             for entry in entries_list:
#                 for name, kwargs in entry.items():
#
#                     loc_name = kwargs['location_name']
#
#                     try:
#                         nested = data[loc_name]
#                     except KeyError:
#                         nested = {'_uid': kwargs.get('location'),
#                                   '_special': True if kwargs.get('location') in ['l00', 'l01', 'l04'] else False,
#                                   'items': [],
#                                   }
#                         data[loc_name] = nested
#
#                     nested['items'].append(kwargs['uid'])
#
#     yaml.dump(data, output)


with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\shoppers.yaml') as f:
    with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\shoppers0.yaml', 'w') as f0:
        for line in f:
            if line[0] == 'a':
                ax, _ = line.split(':')
                i = int(ax[1:])
                ifill = str(i).zfill(2)

                line = f'Aisle {ifill}:\n'

            f0.write(line)
            # f0.write('\n')
