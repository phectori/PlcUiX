class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        # TODO: make itemData a named tuple
        self.itemData = data
        self.childItems = []

    def append_child(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def child_count(self):
        return len(self.childItems)

    def children(self):
        return self.childItems

    def column_count(self):
        return len(self.itemData)

    def item_data(self):  # Todo: Give better name
        return self.itemData

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def set_data(self, column, value):
        try:
            self.itemData[column] = value
        except IndexError:
            return

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def filter(self, re):
        if not re.isValid():
            return True

        for c in self.childItems:
            if c.filter(re):
                return True

        match = re.match(self.data(1))
        return match.hasMatch()
