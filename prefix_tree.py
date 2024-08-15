# Префиксное дерево
# Префиксное дерево — структура данных, позволяющая хранить ассоциативный массив,
# ключами которого чаще всего являются строки.
# Представляет собой корневое дерево, каждое ребро которого помечено каким-то символом так,
# что для любого узла все рёбра, соединяющие этот узел с его сыновьями,
# помечены разными символами.
# Основная идея: реализовать структуру данных для хранения ключевых слов такую,
# чтобы временная сложность поиска слова составляла O(t), где t - длина слова


class Trie:
    def __init__(self):
        self.prefixes = {}
        self.is_word = False

    def insert(self, word: str) -> None:
        if not word:
            self.is_word = True
            return
        if word[0] not in self.prefixes:
            self.prefixes[word[0]] = Trie()
        self.prefixes[word[0]].insert(word[1:])

    def search(self, word: str) -> bool:
        if not word:
            return self.is_word
        if word[0] not in self.prefixes:
            return False
        return self.prefixes[word[0]].search(word[1:])

    def startsWith(self, prefix: str) -> bool:
        if not prefix:
            return True
        if prefix[0] not in self.prefixes:
            return False
        return self.prefixes[prefix[0]].startsWith(prefix[1:])

    def __str__(self, level=0):
        if not self.prefixes:
            return ""
        ret = "\t" * level + repr(self) + "\n"
        for child in self.prefixes.values():
            ret += child.__str__(level + 1)
        return ret

    def __repr__(self):
        return "[" + " ".join(self.prefixes.keys()) + "]"


if __name__ == "__main__":
    obj = Trie()
    obj.insert("cat")
    obj.insert("call")
    obj.insert("car")
    obj.insert("tea")
    obj.insert("teapot")
    print(obj)

    print(f"cat: {obj.search('cat')}")
    print(f"carrot: {obj.search('carrot')}")
    print(f"ca: {obj.search('ca')}")

    print(f"startsWith ca: {obj.startsWith('ca')}")
    print(f"startsWith cat: {obj.startsWith('cat')}")
    print(f"startsWith co: {obj.startsWith('co')}")
