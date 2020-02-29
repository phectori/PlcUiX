from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import Qt
from Models.TreeModel import TreeModel


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FilterModel, self).__init__(parent)
        self.setFilterRole(TreeModel.PathRole)

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 1, source_parent)
        data = self.sourceModel().data(index, Qt.DisplayRole)

        if data == "":
            return True

        return QSortFilterProxyModel.filterAcceptsRow(self, source_row, source_parent)

    #     index = self.sourceModel().index(source_row, 1, source_parent)
    #
    #     data = self.sourceModel().data(index, Qt.DisplayRole)
    #     print(index)
    #     print(data)
    #     print(self.filterRegExp())
    #
    #     if self.filterRegExp().isEmpty():
    #         return True
    #
    #     if self.filterRegExp().isValid():
    #         self.filterRegExp().indexIn(data)
    #         if self.filterRegExp().captureCount() > 0:
    #             return True
    #
    #     return False

    def filterAcceptsColumn(self, source_column, source_parent):
        return True
