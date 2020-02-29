from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from Models.TreeModel import TreeModel


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FilterModel, self).__init__(parent)

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 1, source_parent)
        return index.internalPointer().filter(self.filterRegularExpression())

    def filterAcceptsColumn(self, source_column, source_parent):
        return True
