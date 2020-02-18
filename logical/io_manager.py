"""Separate networking tasks from app"""
import os
import smtplib
import ssl
import time
from datetime import datetime
from socket import socket

import requests
import yaml
from kivymd.app import MDApp

from logical.database import Database
from logical.pools_and_lists import ItemPool, ListWriter
from logical.state import ListState


class IOManager:
    """Common functionality for file managers"""

    def __init__(self, **kwargs):
        """Create default properties, then overwrite them if values are provided"""

        self.username = 'username'
        self.credentials_path = '/credentials.txt'
        self.pools_path = f'data/{self.username}/pools'
        self.old_db_path = f'data/{self.username}/old_database'
        self.lists_path = f'data/{self.username}/lists'
        self.db_path = f'data/{self.username}/{self.username}.yaml'
        self.groups_path = 'data/groups.txt'
        self.stores_path = 'data/stores'

        self.__dict__ = {**self.__dict__, **kwargs}
        self.writer = None
        self.should_update = False

    @staticmethod
    def format_database(database):
        """Convert information stored inside `Database` to yaml-friendly object"""
        all_items = list(database.items.values()) + list(database.new_items.values())
        data = {}

        for item in all_items:
            name = item.name
            uid = item.uid
            group = item.group.uid

            new_defaults = []
            for time_, amount_ in item.defaults:
                try:
                    amount_ = int(amount_)
                except (ValueError, TypeError):
                    amount_ = None
                new_defaults.append([int(round(time_)), amount_])

            note = item.note

            data[uid] = {'group': group,
                         'defaults': new_defaults,
                         'note': note,
                         'name': name,
                         }
        return data

    def make_list(self, item_pool: ItemPool, store_name='shoppers'):
        """Map a store to items"""
        db = MDApp.get_running_app().db
        store = db.stores[store_name]
        self.dump_pool(item_pool)
        self.writer = ListWriter(item_pool, store)
        self.should_update = True

    @staticmethod
    def format_pool(pool: ItemPool):
        """Convert ItemPool to yaml-friendly object"""
        db = MDApp.get_running_app().db
        reformatted_dict = {}
        for key, value in pool.items():
            name, amount, note = value
            try:
                amount = int(amount)
            except (ValueError, TypeError):
                amount = None
            if key not in db.items:
                item = db.new_items[key]
                key = f'{name};{item.group.uid}'
            reformatted_dict[key] = [amount, note]

        return reformatted_dict

    def format_email(self):
        """Done in list writer"""

    @staticmethod
    def _locate_pool(source, date):
        """Helper method for finding pool by filename"""
        for filename in source:
            if date in filename:  # date matches the date of an item list
                return filename

    @staticmethod
    def interpret_pool_data(raw_text):
        """Create a set of items for construction of an `ItemPool` object.
        Lines in files should have the following format:
        `item_uid` OR `item.name`: [`amount`, `note`]
        Item object will be looked up via DB, if not found it is a new/unsorted item and created
        """

        generator_object = yaml.load_all(raw_text, Loader=yaml.Loader)
        db = MDApp.get_running_app().db
        pool = set()
        now = time.time()

        for dict_ in generator_object:
            for uid, info in dict_.items():
                try:
                    item = db.items[uid]
                except KeyError:  # New item created during previous program run
                    amount, note = info
                    name, group = uid.split(';')
                    kwargs = {'name': name,
                              'group': group,
                              'defaults': [(now, amount)],
                              'note': note,
                              }
                    item = db.add_new_item(kwargs)
                else:
                    amount, note = info
                pool.add((item, amount, note))

        return pool

    @property
    def db_save_location(self):
        new_filename = self.get_date(5) + self.username + '.yaml'
        return os.path.join(self.old_db_path, new_filename)

    @staticmethod
    def get_date(length):
        date, dtime = str(datetime.now()).split(" ")
        y, m, d = date.split('-')
        hour, minute, _ = dtime.split(':')
        if length == 5:
            return f'{y}.{m}.{d}.{hour}.{minute}.'
        elif length == 3:
            return f'{y}.{m}.{d}.'
        else:
            raise NotImplementedError(f'Incorrect parameter for method `get_date` {length}')

    def dump_pool(self, item_pool):
        raise NotImplementedError


class NetworkManager(IOManager):
    """Network specific functionality"""

    def __init__(self, **kwargs):
        """Some additional network-only default properties"""

        self.host = '192.168.1.241'
        self.read_port = 42209
        self.send_list_port = 42210
        self.db_port = 42211
        self.pool_port = 42212

        super().__init__(**kwargs)  # Defaults may be overwritten by `super().__init__`

        self.host = '127.0.0.1'  # TODO: remove me

    def dump_database(self):
        """Send updated data to server which will handle renaming old data and saving new data"""
        db = MDApp.get_running_app().db
        data = self.format_database(db)
        s = socket()
        s.connect((self.host, self.db_port))

        with s.makefile(mode='w') as f:
            yaml.dump(data, f)

        s.close()

    def dump_list(self):
        ...  # TODO

    def dump_pool(self, pool):
        """Format pool before saving it to network destination"""
        data = self.format_pool(pool)
        s = socket()
        s.connect((self.host, self.pool_port))

        with s.makefile(mode='w') as f:
            yaml.dump(data, f)

        s.close()

    def send_email(self):
        ...  # TODO

    def _construct_store_pairs(self):
        """Generate paired values for creating store objects from network location"""
        # stores_path = f'http://{self.host}:{self.read_port}/stores/shoppers.yaml'
        # with requests.get(stores_path) as f:
        #     c = f.content.decode()
        #     print(c)
        # return 'shoppers', yaml.load(c, Loader=yaml.Loader)

        stores_path = f'http://{self.host}:{self.read_port}/stores'
        listing = ''.join(chunk.decode() for chunk in requests.get(stores_path))
        lines = listing.split('\n')
        for line in lines:
            if '.yaml' in line:
                _, filename, _ = line.split('"')
                print(os.path.join(stores_path, filename))
                name, ext = filename.split('.')
                with requests.get(f'{stores_path}/{filename}') as f:
                    content = f.content.decode()
                print(content)
                mapping = yaml.load(content, Loader=yaml.Loader)
                yield name, mapping

    def load_databse(self):
        """Get sources for groups, stores, and items via network; use them to construct `Database.`"""

        groups_path = f'http://{self.host}:{self.read_port}/groups.txt'
        r = requests.get(groups_path)
        groups_raw = r.content.decode()
        groupnames = [n for n in groups_raw.split('\n') if n]
        print(groupnames)

        stores = {k: v for k, v in self._construct_store_pairs()}

        db_path = f'http://{self.host}:{self.read_port}/{self.username}/{self.username}.yaml'
        content = requests.get(db_path).content
        items = yaml.load(content, Loader=yaml.Loader)

        return Database(groups=groupnames,
                        stores=stores,
                        items=items,
                        )

    def locate_pool(self, date=None, return_names=False,):
        """Check a network location for a list in progress containing today's date"""

        items = ''
        pools_path = f'http://{self.host}:{self.read_port}/username/pools'
        r = requests.get(pools_path)

        for file in r:
            items += str(file.decode())

        if return_names:
            return items

        return self._locate_pool(items.split('\n'), date)

    def load_pool(self, date=None):
        """If we find a pool in progress in the network location, load it."""

        if not date:
            date = self.get_date(3)
        if not (self.locate_pool(date)):
            return  # No pool matching date

        network_path = f'http://{self.host}:{self.read_port}/{self.username}/pools/{date}itempool.yaml'
        with requests.get(network_path) as req:
            content = req.content.decode()
        pool_params = self.interpret_pool_data(content)
        ListState.instance.populate_from_pool(ItemPool(pool_params))


class LocalManager(IOManager):
    """Windows specific functionality"""

    def dump_database(self):
        """Rename current database file before saving updated data to local filesystem"""
        db = MDApp.get_running_app().db
        data = self.format_database(db)
        new_filename = self.db_save_location
        os.rename(self.db_path, new_filename)
        with open(self.db_path, 'w') as f:
            yaml.dump(data, f)

    def dump_list(self, pool):
        """Write list to plaintext format"""
        self.make_list(pool)
        self.writer.format_plaintext()

        filename = self.get_date(3) + 'ShoppingList.txt'

        write_destination = os.path.join(self.lists_path, filename)

        with open(write_destination, 'w') as f:
            f.write(self.writer.content)
        return 'List Saved.'

    def dump_pool(self, pool: ItemPool):
        """Format pool before saving it to local filesystem"""
        data = self.format_pool(pool)
        filename = os.path.join(self.pools_path, self.get_date(3) + 'itempool.yaml')
        with open(filename, 'w') as f:
            yaml.dump(data, f)

        return 'Items saved to disk.'

    def print_list(self, pool):
        """Option to start printing (Windows only)."""
        self.dump_list(pool)
        filename = self.get_date(3) + 'ShoppingList.txt'
        write_destination = os.path.join(self.lists_path, filename)
        os.startfile(write_destination, 'print')
        return 'List saved;\n printing in progress'

    def send_email(self, pool):
        """Read login info from credentials and access server to send email"""
        self.make_list(pool)
        self.dump_list(pool)

        with open('data\\credentials.txt') as f:
            sender_email, receiver_email, password = [line.split(':')[1][:-1] for line in f]

        port = 465  # For SSL
        context = ssl.create_default_context()  # Create a secure SSL context
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, self.writer.email_content)

        return 'List sent via Email.'

    def _construct_store_pairs(self):
        """Generate paired values for creating store objects"""
        for root, _, filenames in os.walk(os.path.join(os.getcwd(), self.stores_path)):
            for filename in filenames:
                name, ext = filename.split('.')
                with open(os.path.join(root, filename)) as file:
                    mapping = yaml.load(file, Loader=yaml.Loader)
                    yield name, mapping

    def load_databse(self):
        """Get sources for groups, stores, and items via local filesystem;
        Use sources to construct `Database.`
        """
        with open(self.groups_path) as f:
            groups_raw = f.read()
            groupnames = groups_raw.split('\n')
        stores = {k: v for k, v in self._construct_store_pairs()}

        with open(self.db_path) as f:
            items = yaml.load(f, Loader=yaml.Loader)

        return Database(groups=groupnames,
                        stores=stores,
                        items=items,
                        )

    def locate_pool(self, date=None, return_names=False, ):
        """Check local filesystem for a pool in progress"""

        root, dirs, filenames = next(os.walk(self.pools_path))
        if return_names:
            return filenames
        return self._locate_pool(filenames, date)

    def load_pool(self, date=None):
        """If we find a pool in progress in the local filesystem, load it."""
        if not date:
            date = self.get_date(3)
        if not (file := self.locate_pool(date)):
            return  # No pool matching date
        filepath = os.path.join(self.pools_path, file)

        with open(filepath) as f:
            content = f.read()
            # print(content)
            pool_params = self.interpret_pool_data(content)
            ListState.instance.populate_from_pool(ItemPool(pool_params))

















