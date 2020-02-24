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


class SettingsManager:
    """Separation of concerns between storing info needed for coordinating I/O and executing IO operations"""

    def __init__(self,
                 username='username',
                 groups_path='data/groups.txt',
                 stores_path='data/stores',
                 credentials_path=None,
                 pools_path=None,
                 old_db_path=None,
                 lists_path=None,
                 db_path=None,
                 default_store=None,
                 host='127.0.0.1',
                 read_port=42209,
                 write_port=42210,
                 rename_port=42211,
                 merge_always=None,
                 merge_once=None,
                 write_new_items=False,
                 **kwargs
                 ):

        # Basic properties
        self.username = username
        self.groups_path = groups_path
        self.stores_path = stores_path
        self.default_store = default_store

        # Network properties
        self.host = host
        self.read_port = read_port
        self.write_port = write_port
        self.rename_port = rename_port

        # Can be replaced with custom values or inferred using @property decorator
        self._credentials_path = credentials_path
        self._pools_path = pools_path
        self._old_db_path = old_db_path
        self._lists_path = lists_path
        self._db_path = db_path

        # Other advanced properties
        self.merge_always = merge_always
        self.merge_once = merge_once
        self._other_kwargs = kwargs
        self.write_new_items = write_new_items

    @property
    def credentials_path(self):
        if not self._credentials_path:
            self._credentials_path = f'data/{self.username}/credentials.txt'
        return self._credentials_path

    @property
    def pools_path(self):
        if not self._pools_path:
            self._pools_path = f'data/{self.username}/pools'
        return self._pools_path

    @property
    def old_db_path(self):
        if not self._old_db_path:
            self._old_db_path = f'data/{self.username}/old_database'
        return self._old_db_path

    @property
    def lists_path(self):
        if not self._lists_path:
            self._lists_path = f'data/{self.username}/lists'
        return self._lists_path

    @property
    def db_path(self):
        if not self._db_path:
            self._db_path = f'data/{self.username}/{self.username}.yaml'
        return self._db_path

    @property
    def db_save_location(self):
        new_filename = self.get_date(5) + self.username + '.yaml'
        return os.path.join(self.old_db_path, new_filename)

    @staticmethod
    def preload_settings(path, kwargs):
        """Check a location for settings, use them to update our keyword-value pairs"""
        filepath = os.path.join(os.getcwd(), path)
        with open(filepath) as f:
            new_defaults = yaml.load(f, Loader=yaml.Loader)
        kwargs.update(new_defaults)
        return kwargs

    @staticmethod
    def get_date(len_):
        date_, time_ = str(datetime.now()).split(" ")
        y, m, d = date_.split('-')
        hour, minute, _ = time_.split(':')
        if len_ == 5:
            return f'{y}.{m}.{d}.{hour}.{minute}.'
        elif len_ == 3:
            return f'{y}.{m}.{d}.'
        else:
            raise ValueError(f'Invalid parameter: {len_}')


class IOManager(SettingsManager):
    """Common functionality for file managers"""

    def __init__(self):
        kwargs = self.preload_settings('data/global_settings.yaml', {})
        if path_ := kwargs.get('user_settings_location'):
            kwargs = self.preload_settings(path_, kwargs)
        super().__init__(**kwargs)  # `kwargs` has been updated with user values supplied form global/user settings

        self.writer = None  # List formatting object
        self.should_update = False  # Whether or not to update database with new values

    def format_database(self, database):
        """Convert information stored inside `Database` to yaml-friendly object"""
        all_items = list(database.items.values())
        if self.write_new_items:
            all_items += list(database.new_items.values())
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

    def make_list(self, item_pool: ItemPool, store_name=None):
        """Map a store to items"""
        if not store_name:
            store_name = 'default'

        db = MDApp.get_running_app().db
        store = db.stores[store_name]
        self.dump_pool(item_pool)
        if self.merge_always or self.merge_once:
            item_pool = self.mix_pools(item_pool)
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
    def _locate_pool_by_date(source, date):
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
                    item_str, group = uid.split(';')
                    name, uid = item_str.rsplit(' ', maxsplit=1)
                    kwargs = {'name': name,
                              'group': group,
                              'defaults': [(now, amount)],
                              'note': note,
                              'uid': uid[1:-1],
                              }
                    item = db.add_new_item(kwargs)
                else:
                    amount, note = info
                pool.add((item, amount, note))

        return pool

    def dump_pool(self, item_pool):
        raise NotImplementedError

    def load_pool(self, **kwargs):
        raise NotImplementedError

    def mix_pools(self, base):
        raise NotImplementedError


class NetworkManager(IOManager):
    """Network specific functionality"""

    def dump_database(self):
        """Send updated data to server which will handle renaming old data and saving new data"""
        db = MDApp.get_running_app().db
        data = self.format_database(db)
        s0 = socket()
        s0.connect((self.host, self.rename_port))
        with s0.makefile(mode='w') as f:
            f.write('::'.join((self.db_path, self.db_save_location)))

        s1 = socket()
        s1.connect((self.host, self.write_port))
        body = yaml.dump(data)
        full_text = '::'.join((self.db_path, body))
        with s1.makefile(mode='w') as f:
            f.write(full_text)

        s1.close()

    def dump_list(self):
        ...  # TODO

    def dump_pool(self, pool):
        """Format pool before saving it to network destination"""
        data = self.format_pool(pool)
        s = socket()
        s.connect((self.host, self.write_port))

        body = yaml.dump(data)
        filename = os.path.join(self.pools_path, self.get_date(3) + 'itempool.yaml')
        full_text = '::'.join((filename, body))

        with s.makefile(mode='w') as f:
            f.write(full_text)

        s.close()

    def send_email(self):
        ...  # TODO

    def _construct_store_pairs(self):
        """Generate paired values for creating store objects from network location"""

        stores_path = f'http://{self.host}:{self.read_port}/stores'
        listing = ''.join(chunk.decode() for chunk in requests.get(stores_path))
        lines = listing.split('\n')
        for line in lines:
            if '.yaml' in line:
                _, filename, _ = line.split('"')
                name, ext = filename.split('.')
                with requests.get(f'{stores_path}/{filename}') as f:
                    content = f.content.decode()
                mapping = yaml.load(content, Loader=yaml.Loader)
                yield name, mapping

    def create_database(self):
        """Get sources for groups, stores, and items via network; use them to construct `Database.`"""

        groups_path = f'http://{self.host}:{self.read_port}/groups.txt'
        r = requests.get(groups_path)
        groups_raw = r.content.decode()
        groupnames = [n for n in groups_raw.split('\n') if n]

        stores = {k: v for k, v in self._construct_store_pairs()}

        db_path = f'http://{self.host}:{self.read_port}/{self.username}/{self.username}.yaml'
        content = requests.get(db_path).content
        items = yaml.load(content, Loader=yaml.Loader)

        return Database(groups=groupnames,
                        stores=stores,
                        items=items,
                        default_store=self.default_store,
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

        return self._locate_pool_by_date(items.split('\n'), date)

    def load_pool(self, netpath=None, date=None):
        """If we receive a network path parameter, load that pool.
        If not, look for a pool matching the date provided, or today's date, if none is provided.
        If we find a matching pool in progress in the network location, load it.
        """

        if netpath:
            network_path = netpath
        else:
            if not date:
                date = self.get_date(3)
            if not (self.locate_pool(date)):
                return  # No pool matching date
            network_path = f'http://{self.host}:{self.read_port}/{self.username}/pools/{date}itempool.yaml'

        with requests.get(network_path) as req:
            content = req.content.decode()
        pool_params = self.interpret_pool_data(content)
        ListState.instance.populate_from_pool(ItemPool(pool_params))

    def mix_pools(self, base):
        ...  # TODO


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

        with open(self.credentials_path) as f:
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

    def create_database(self):
        """Get sources for groups, stores, and items via local filesystem;
        Use sources to construct `Database.`
        """
        with open(self.groups_path) as f:  # Build data for groups
            groups = f.read().split('\n')

        stores = {k: v for k, v in self._construct_store_pairs()}  # Build data for stores

        with open(self.db_path) as f:  # Build data for items
            items = yaml.load(f, Loader=yaml.Loader)

        return Database(groups=groups,
                        stores=stores,
                        items=items,
                        default_store=self.default_store,
                        )

    def locate_pool(self, date=None, return_names=False, ):
        """Check local filesystem for a pool in progress"""

        root, dirs, filenames = next(os.walk(self.pools_path))
        if return_names:
            return root, filenames
        return self._locate_pool_by_date(filenames, date)

    def load_pool(self, filename=None, date=None):
        """If we receive a filename parameter, load that pool.
        If not, look for a pool matching the date provided, or today's date, if none is provided.
        If we find a matching pool in progress in the local filesystem, load it.
        """

        if filename:
            filepath = filename
        else:
            if not date:
                date = self.get_date(3)
            if not (file := self.locate_pool(date)):
                return  # No pool matching date
            filepath = os.path.join(self.pools_path, file)

        with open(filepath) as f:
            content = f.read()
            pool_params = self.interpret_pool_data(content)
            return ItemPool(pool_params)

    def mix_pools(self, base: ItemPool):
        """Load and merge pools based on user settings"""

        always_ = self.load_pool(filename=self.merge_always) if self.merge_always else None
        if self.merge_once:
            root, _, file = next(os.walk(self.merge_once))
            try:
                filepath = os.path.join(root, file[0])
            except IndexError:
                once_ = None
            else:
                once_ = self.load_pool(filename=filepath)
                os.remove(filepath)
        else:
            once_ = None
        base += always_
        base += once_

        return base
