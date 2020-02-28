from PyQt5.QtCore import QSortFilterProxyModel, Qt


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FilterModel, self).__init__(parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):

        index = self.sourceModel().index(sourceRow, 1, sourceParent)
        print(self.sourceModel().data(index, Qt.DisplayRole))
        # rowCount = self.sourceModel().rowCount(index)
        # return QSortFilterProxyModel.filterAcceptsRow(self, sourceRow, sourceParent)
        return True

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return True

