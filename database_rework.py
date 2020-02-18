from logical.database import Database

# def local(self):
#     abs_path = os.path.join(os.getcwd(), self.path)
#     filename = f'{self.get_date()}{self.username}.{self.ext}'
#     db_copy_destination = os.path.join(abs_path, 'old_database')
#     new_filepath = os.path.join(db_copy_destination, filename)
#     os.rename(self.filepath, new_filepath)
#
#     with open(self.filepath, 'w') as f:
#         dump(self, f)


# def dump(self, f):
#     all_items = list(self.items.values()) + list(self.new_items.values())
#     data = {}
#
#     for item in all_items:
#         name = item.name
#         uid = item.uid
#         group = item.group.uid
#
#         new_defaults = []
#         for time_, amount_ in item.defaults:
#             try:
#                 amount_ = int(amount_)
#             except (ValueError, TypeError):
#                 amount_ = None
#             new_defaults.append([int(round(time_)), amount_])
#
#         note = item.note
#
#         data[uid] = {'group': group,
#                      'defaults': new_defaults,
#                      'note': note,
#                      'name': name,
#                      }
#
#     yaml.dump(data, f, allow_unicode=True)


db = Database('data/username/username.yaml')

# local(db)
