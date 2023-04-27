import pickle
from os.path import exists
from collections import OrderedDict


class Cache(OrderedDict):
    def __init__(self, file_path, protocol=pickle.HIGHEST_PROTOCOL, capacity=-1, mru=True):
        super().__init__()
        self.file_path = file_path
        self.protocol = protocol
        self.capacity = capacity
        self.mru = mru

    def save(self):
        with open(self.file_path, 'wb') as file:
            pickle.dump(self, file, protocol=self.protocol)

    def resize(self, new_capacity):
        self.capacity = new_capacity
        while len(self) > self.capacity-1 >= 0:
            self.popitem(last=False)

    def __setitem__(self, key, value):
        self.resize(self.capacity)
        super().__setitem__(key, value)

    def __getitem__(self, item):
        value = super().__getitem__(item)
        if self.mru and item in self:
            del self[item]
            self[item] = value  # If a value is queried, reset its eviction priority (index)
        return value

    def __reduce__(self):
        # https://stackoverflow.com/questions/45860040/pickling-a-subclass-of-an-ordereddict
        state = super().__reduce__()
        new_state = (state[0],
                     ([],),
                     self.__dict__,
                     None,
                     state[4])
        return new_state


def make_cache(file, protocol=pickle.HIGHEST_PROTOCOL, capacity=-1, mru=True, verbose=False, prefer_saved_properties=False) -> Cache:
    if not exists(file):
        if verbose:
            print(f'Making cache file: {file} with protocol={protocol}, mru={mru}, and capacity={capacity}')
        cache = Cache(file, protocol=protocol, capacity=capacity, mru=mru)
        cache.save()
        return cache
    with open(file, 'rb') as file:
        cache = pickle.load(file)
        if prefer_saved_properties:
            cache.protocol = protocol
            cache.mru = mru
            cache.resize(capacity)
        return cache
