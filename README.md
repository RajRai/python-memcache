# python-memcache
A  lightweight, local memcache for python. Supports persistence, MRU mode, and max capacity selection.

The cache is only written to the disk on calls to `save()` to minimize overhead for basic operations in calling applications.

The entire cache is saved on calls to `save()`. If you want to save access entries only, try a `shelve`, or a different solution.

You can resize the cache either with `resize(new_capacity)`, or by accessing the `capacity` property directly.
If you do it with the `capacity` property, the actual resize will only reliably happen the next time a value is stored to the cache. 
For MRU caches, it will also happen when a value is requested, since that updates its location in the cache.

Properties of the cache, like its capacity and MRU setting, are saved along with the cache data with calls to `save()`. 
However, when calling `make_cache`, the keyword arguments `protocol`, `capacity`, and `mru` will override whatever has been previously saved with calls to `Cache.save()`.
To prevent this, set `prefer_saved_properties=True` when calling `make_cache`, and the properties saved to the cache file will override the keyword arguments, which will only be used for new caches.
