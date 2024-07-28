from copy import deepcopy
from returns.maybe import Maybe, Some, Nothing
from typing import Optional


class frozendict[K, V]:
    """
    An immutable wrapper around a mutable dict.

    This class provides an immutable dictionary-like object. Once created, the dictionary cannot be modified.
    It supports standard dictionary operations and some additional methods for immutability and safe usage.
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes a frozendict instance with the given arguments.

        Args:
            *args: Positional arguments passed to the dictionary constructor.
            **kwargs: Keyword arguments passed to the dictionary constructor.
        """
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key: K) -> V:
        """
        Retrieves the value associated with the given key.

        Args:
            key: The key to look up in the dictionary.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key is not found in the dictionary.
        """
        return self._dict[key]

    def get(self, key: K) -> Optional[V]:
        """
        Retrieves the value associated with the given key, or None if the key is not found.

        Args:
            key: The key to look up in the dictionary.

        Returns:
            The value associated with the key, or None if the key is not found.
        """
        item = self._dict.get(key)
        if item is not None:
            return item
        return None

    def get_maybe(self, key: K) -> Maybe[V]:
        """
        Retrieves the value associated with the given key as a Maybe type.

        Args:
            key: The key to look up in the dictionary.

        Returns:
            A Maybe instance containing the value if the key is found, or Nothing if the key is not found.
        """
        item = self._dict.get(key)
        if item is not None:
            return Some(item)
        return Nothing

    def __eq__(self, other) -> bool:
        """
        Checks if the current frozendict is equal to another dictionary or frozendict.

        Args:
            other: The object to compare with the current frozendict.

        Returns:
            True if the other object is equal to the current frozendict, False otherwise.
        """
        match other:
            case frozendict():
                return self._dict == other._dict
            case dict():
                return self._dict == other
            case _:
                return False

    def __contains__(self, key) -> bool:
        """
        Checks if the dictionary contains the given key.

        Args:
            key: The key to check for in the dictionary.

        Returns:
            True if the key is present in the dictionary, False otherwise.
        """
        return key in self._dict

    def __len__(self) -> int:
        """
        Returns the number of items in the dictionary.

        Returns:
            The number of key-value pairs in the dictionary.
        """
        return len(self._dict)

    def keys(self):
        """
        Returns an iterator over the dictionary's keys.

        Returns:
            An iterator over the keys of the dictionary.
        """
        return self._dict.keys()

    def values(self):
        """
        Returns an iterator over the dictionary's values.

        Returns:
            An iterator over the values of the dictionary.
        """
        return self._dict.values()

    def items(self):
        """
        Returns an iterator over the dictionary's key-value pairs.

        Returns:
            An iterator over the key-value pairs of the dictionary.
        """
        return self._dict.items()

    def __iter__(self):
        """
        Returns an iterator over the dictionary's keys.

        Returns:
            An iterator over the keys of the dictionary.
        """
        return iter(self._dict)

    def __repr__(self) -> str:
        """
        Returns a string representation of the frozendict instance.

        Returns:
            A string representation of the frozendict.
        """
        return f"frozendict({self._dict})"

    def __str__(self) -> str:
        """
        Returns a string representation of the frozendict instance.

        Returns:
            A string representation of the frozendict.
        """
        return f"frozendict({self._dict})"

    def __hash__(self) -> int:
        """
        Returns the hash value of the frozendict.

        The hash is computed based on the key-value pairs in the dictionary.
        This method ensures that the hash value is consistent for the lifetime
        of the frozendict.

        Returns:
            The hash value of the frozendict.
        """
        if self._hash is None:
            h = 0
            for key, value in self._dict.items():
                h ^= hash((key, value))
            self._hash = h
        return self._hash

    def put(self, k: K, v: V) -> "frozendict":
        """
        Returns a new frozendict with an updated value for the given key.

        This method creates a new frozendict instance with the same contents as the current instance, but with
        the value for the specified key updated.

        Args:
            k: The key to update.
            v: The new value for the key.

        Returns:
            A new frozendict instance with the updated value.
        """
        new_dict = deepcopy(self._dict)
        new_dict[k] = v
        return frozendict(new_dict)

    def combine(self, other) -> "frozendict":
        """
        Combines the current frozendict with another frozendict.

        This method returns a new frozendict that contains all key-value pairs
        from both frozendicts. If there are duplicate keys,
        the values from the other frozendict will overwrite the values
        from the current frozendict.

        Args:
            other: The other frozendict to combine with.

        Returns:
            A new frozendict containing all key-value pairs from both frozendicts.
        """
        return frozendict({**self.raw, **other.raw})

    @property
    def raw(self) -> dict:
        """
        Gets the underlying dictionary in its raw form.

        Returns:
            The underlying dictionary.
        """
        return self._dict

    @classmethod
    def fromkeys(cls, *args, **kwargs) -> "frozendict":
        """
        Creates a new frozendict with keys from the given iterable
        and values set to a specified value.

        Args:
            *args: Positional arguments passed to the dict.fromkeys method.
            **kwargs: Keyword arguments passed to the dict.fromkeys method.

        Returns:
            A new frozendict with the specified keys and values.
        """
        return cls(dict.fromkeys(*args, **kwargs))

    @staticmethod
    def new() -> "frozendict":
        """
        Creates a new, empty frozendict.

        Returns:
            A new, empty frozendict.
        """
        return frozendict()

    @staticmethod
    def combine_dicts(fd1, fd2) -> "frozendict":
        """
        Combines two frozendicts into a new frozendict.

        This method returns a new frozendict that contains all key-value pairs
        from both frozendicts. If there are duplicate keys,
        the values from the second frozendict will overwrite the values
        from the first frozendict.

        Args:
            fd1: The first frozendict.
            fd2: The second frozendict.

        Returns:
            A new frozendict containing all key-value pairs from both frozendicts.
        """
        return fd1.combine(fd2)
