from logical.database import Database

db = Database(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\username.yaml')


body = '\n'.join([f'{uid}:{item.name}:l05:Aisle 05:FALSE' for uid, item in db.items.items()])

for store in ['giant', 'shoppers', 'safeway', 'hmart', 'lidl']:
    storename = f'\\{store}.txt'
    with open(r'C:\Users\Oliver\PycharmProjects\groceriesv3\data\_stores' + storename, 'w') as f:
        f.write(body)
        f.write('\n')
