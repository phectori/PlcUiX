from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from TreeItem import TreeItem
from AdsClient import AdsClient


class TreeModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(("Name", "Type", "Size", "Comment"))

    def columnCount(self, parent=None, *args, **kwargs):
        if parent.isValid():
            return parent.internalPointer().column_count()
        else:
            return self.rootItem.column_count()

    def data(self, index, role=None):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent=None, *args, **kwargs):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent()

        if parent_item == self.rootItem:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        return parent_item.child_count()

    def populate(self, entries):
        for e in entries:
            self.append_descriptor_entry(e)

    def append_descriptor_entry(self, entry: AdsClient.VariableDescriptionEntry):
        self._append_descriptor_entry_helper(
            entry.name.split("."), self.rootItem, entry
        )

    # Recursive append
    def _append_descriptor_entry_helper(
        self,
        items: list,
        parent: TreeItem,
        ads_entry: AdsClient.VariableDescriptionEntry,
    ):
        if len(items) > 1:
            # Check if item exists first, TODO: this should be a function in TreeItem (e.g. has_child())
            filtered = list(
                filter(lambda x: x.item_data()[0] == items[0], parent.children())
            )

            if len(filtered) == 0:
                node = TreeItem((items[0], "", "", "", ""), parent)
                parent.append_child(node)
            else:
                node = filtered[0]

            self._append_descriptor_entry_helper(items[1:], node, ads_entry)
        elif len(items) == 1:
            name = items[0]
            parent.append_child(
                TreeItem((name, ads_entry.typename, ads_entry.datatype_size, ads_entry.comment), parent)
            )