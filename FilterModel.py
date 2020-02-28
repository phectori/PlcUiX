from PyQt5.QtCore import QSortFilterProxyModel, Qt


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(FilterModel, self).__init__(parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        print(self.sourceModel().data(sourceRow))
        # index = self.sourceModel().index(sourceRow, 0, sourceParent)
        # rowCount = self.sourceModel().rowCount(index)
        # return QSortFilterProxyModel.filterAcceptsRow(self, sourceRow, sourceParent)
        return True

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        return True

