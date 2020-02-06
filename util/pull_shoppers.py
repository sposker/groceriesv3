import yaml

data = {}

with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\shoppers.yaml', 'w') as output:
    with open('shoppers locs.yaml') as f:
        for entries_list in yaml.load_all(f, Loader=yaml.Loader):
            for entry in entries_list:
                for name, kwargs in entry.items():

                    loc_name = kwargs['location_name']

                    try:
                        nested = data[loc_name]
                    except KeyError:
                        nested = {'_uid': kwargs.get('location'),
                                  '_special': True if kwargs.get('location') in ['l00', 'l01', 'l04'] else False,
                                  'items': [],
                                  }
                        data[loc_name] = nested

                    nested['items'].append(kwargs['uid'])

    yaml.dump(data, output)
