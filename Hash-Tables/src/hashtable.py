# '''
# Linked List hash table key/value pair
# '''


class LinkedPair:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    '''
    A hash table that with `capacity` buckets
    that accepts string keys
    '''
    def __init__(self, capacity):
        self.capacity = capacity  # Number of buckets in the hash table
        self.storage = [None] * capacity

    def _hash(self, key):
        '''
        Hash an arbitrary key and return an integer.

        You may replace the Python hash with DJB2 as a stretch goal.
        '''
        return hash(key)

    def _hash_djb2(self, key):
        '''
        Hash an arbitrary key using DJB2 hash

        OPTIONAL STRETCH: Research and implement DJB2
        '''
        pass

    def _hash_mod(self, key):
        '''
        Take an arbitrary key and return a valid integer index
        within the storage capacity of the hash table.
        '''
        return self._hash(key) % self.capacity

    def insert(self, key, value):
        '''
        Store the value with the given key.

        Hash collisions should be handled with Linked List Chaining.

        Fill this in.
        '''
        index = self._hash_mod(key)
        node = self.storage[index]

        # Traverse SLL of keys w/ same index
        while (node is not None and node.key != key):
            last_node = node
            node = last_node.next

        # Overwrite value if node, key exists
        # Else create new LL node at index
        if node is not None:
            node.value = value
        else:
            new_node = LinkedPair(key, value)
            new_node.next = self.storage[index]
            self.storage[index] = new_node

    def remove(self, key):
        '''
        Remove the value stored with the given key.
        Print a warning if the key is not found.
        Fill this in.
        '''
        index = self._hash_mod(key)
        node = self.storage[index]
        last_node = None

        while (node is not None and node.key != key):
            last_node = node
            node = last_node.next

        # If node doesn't exist error out
        if node is None:
            print(f'ERROR: Unable to remove key {key}')
        else:
            # If node is head
            if last_node is None:
                self.storage[index] = node.next
            else:
                last_node.next = node.next

    def retrieve(self, key):
        '''
        Retrieve the value stored with the given key.
        Returns None if the key is not found.
        Fill this in.
        '''
        index = self._hash_mod(key)
        node = self.storage[index]

        while (node is not None):
            if (node.key == key):
                return node.value
            node = node.next

        return None

    def resize(self):
        '''
        Doubles the capacity of the hash table and
        rehash all key/value pairs.
        Fill this in.
        '''
        self.capacity *= 2
        new_ht = HashTable(self.capacity)

        for node in self.storage:
            if node is not None:
                while (node is not None):
                    new_ht.insert(node.key, node.value)
                    node = node.next
        self.storage = new_ht.storage


if __name__ == "__main__":
    ht = HashTable(2)

    ht.insert("line_1", "Tiny hash table")
    ht.insert("line_2", "Filled beyond capacity")
    ht.insert("line_3", "Linked list saves the day!")

    print("")

    # Test storing beyond capacity
    print(ht.retrieve("line_1"))
    print(ht.retrieve("line_2"))
    print(ht.retrieve("line_3"))

    # Test resizing
    old_capacity = len(ht.storage)
    ht.resize()
    new_capacity = len(ht.storage)

    print(f"\nResized from {old_capacity} to {new_capacity}.\n")

    # Test if data intact after resizing
    print(ht.retrieve("line_1"))
    print(ht.retrieve("line_2"))
    print(ht.retrieve("line_3"))

    print("")
