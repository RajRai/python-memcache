import pickle
from os.path import exists
from collections import OrderedDict


class Cache(OrderedDict):
    def __init__(self, file, protocol=pickle.HIGHEST_PROTOCOL, n=-1):
        super().__init__()
        self.file = file
        self.protocol = protocol
        self.n = n

    def save(self):
        with open(self.file, 'wb') as file:
            pickle.dump(self, file, protocol=self.protocol)

    def __setitem__(self, key, value):
        if len(self) > self.n-1 > 0:
            self.popitem(last=False)
        super().__setitem__(key, value)

    def __getitem__(self, item):
        value = super().__getitem__(item)
        if item in self:
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


def make_cache(file, protocol=pickle.HIGHEST_PROTOCOL, n=-1, verbose=False) -> Cache:
    if not exists(file):
        if verbose:
            print(f'Making cache file: {file} with protocol {protocol} and n={n}')
        cache = Cache(file, protocol=protocol, n=n)
        cache.save()
        return cache
    with open(file, 'rb') as file:
        return pickle.load(file)
