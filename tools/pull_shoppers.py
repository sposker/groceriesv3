from logical.database import Database
import yaml

with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\shoppers.yaml') as f:
    mapping = yaml.load(f, Loader=yaml.Loader)
    db = Database(build_empty=True)
    db.build_stores({'shoppers': mapping})
    print([k for k in db.stores])
    refactored = {}
    with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\stores\shoppers0.yaml', 'w') as f0:
        for storename, store in db.stores.items():
            print(store.locations)
            for loc in store.locations.values():
                refactored[loc.uid] = {'_name': loc.name, '_is_special': loc.is_special, 'items': list(loc.items)}
            yaml.dump(refactored, f0)
