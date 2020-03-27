class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.spam_count = 0
        self.normal_count = 0


class Trie:

    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.root = TrieNode()


    def insert(self, word: str, label: int) -> None:
        """
        Inserts a word into the trie.
        """
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_word = True
        if label == 1:
            node.spam_count += 1
        else:
            node.normal_count += 1


    def search(self, word: str):
        """
        Returns if the word is in the trie.
        """
        node = self.root

        for c in word:

            if c in node.children:
                node = node.children[c]
            else:
                return None
        return node if node.is_word else None


    def startsWith(self, prefix: str) -> bool:
        """
        Returns if there is any word in the trie that starts with the given prefix.
        """
        node = self.root

        for c in prefix:

            if c in node.children:
                node = node.children[c]
            else:
                return False
        return True
