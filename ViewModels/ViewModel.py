from PyQt5.QtCore import pyqtProperty, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtQml import qmlRegisterType
from Models.AdsClient import AdsClient
from Models.TreeModel import TreeModel
from Models.FilterModel import FilterModel


class ViewModel(QObject):
    filterModelChanged = pyqtSignal()

    def __init__(self, ads_client, parent=None):
        super().__init__(parent)
        self.application_name = "Plc UiX"

        # Register the types
        qmlRegisterType(FilterModel, "FilterModel", 1, 0, "FilterModel")
        qmlRegisterType(TreeModel, "TreeModel", 1, 0, "TreeModel")

        # ads_client = AdsClient(args.ams_net_id, args.ams_net_port, lnp_client)
        self.ads_client = ads_client
        self.entries = self.ads_client.get_ads_entries()

        if len(self.entries) == 0:
            self.entries.append(
                AdsClient.VariableDescriptionEntry(
                    "TESTING.test", "BOOL", "This is a comment", 1, 1
                )
            )
            self.entries.append(
                AdsClient.VariableDescriptionEntry(
                    "TESTING.test1", "BOOL", "This is also a comment", 1, 1
                )
            )

        self.tree_model = TreeModel()
        self.tree_model.populate(self.entries)

        self.filter_model = FilterModel()
        self.filter_model.setSourceModel(self.tree_model)
        self.filterModelChanged.emit()

    @pyqtProperty("QString", constant=True)
    def name(self):
        return self.application_name

    @pyqtProperty(FilterModel, notify=filterModelChanged)
    def model(self):
        return self.filter_model

    @pyqtSlot("QModelIndex")
    def on_double_clicked(self, index):
        name = index.data(TreeModel.PathRole)
        typ = index.data(TreeModel.TypeRole)
        self.ads_client.subscribe_by_name(name, typ)
