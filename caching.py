import pickle
from os.path import exists


class Cache(dict):
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
        while len(self) > self.capacity - 1 >= 0:
            del self[next(iter(self))]

    def __setitem__(self, key, value):
        self.resize(self.capacity)
        super().__setitem__(key, value)

    def __getitem__(self, item):
        value = super().__getitem__(item)
        if self.mru and item in self:
            del self[item]
            self[item] = value  # If a value is queried, reset its eviction priority (index)
        return value

    # The next 3 methods are needed because we're trying to pickle a subclass of dict, which is a weird case
    # https://stackoverflow.com/questions/21144845/how-can-i-unpickle-a-subclass-of-dict-that-validates-with-setitem-in-pytho
    def __getstate__(self):
        # Return the state to be pickled
        state = self.__dict__.copy()
        state['data'] = dict(self)
        return state

    def __setstate__(self, state):
        # Restore the state when unpickling
        self.__init__(state['file_path'], state['protocol'], state['capacity'], state['mru'])
        self.update(state['data'])

    def __reduce__(self):
        return self.__class__, (self.file_path, self.protocol, self.capacity, self.mru), self.__getstate__()


def make_cache(file, protocol=pickle.HIGHEST_PROTOCOL, capacity=-1, mru=True, verbose=False,
               ignore_saved_properties=False) -> Cache:
    if not exists(file):
        if verbose:
            print(f'Making cache file: {file} with protocol={protocol}, mru={mru}, and capacity={capacity}')
        cache = Cache(file, protocol=protocol, capacity=capacity, mru=mru)
        cache.save()
        return cache
    with open(file, 'rb') as file:
        cache = pickle.load(file)
        if ignore_saved_properties:
            cache.protocol = protocol
            cache.mru = mru
            cache.resize(capacity)
        return cache
