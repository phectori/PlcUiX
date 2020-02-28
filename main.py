from lognplot.client import LognplotTcpClient
from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from TreeModel import TreeModel
from FilterModel import FilterModel
from AdsClient import AdsClient
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--ams-net-id", help="ams net id", default="127.0.0.1.1.1", type=str
    )
    parser.add_argument("--ams-net-port", help="ams net port", default=851, type=int)
    parser.add_argument("--lognplot-hostname", default="localhost", type=str)
    parser.add_argument("--lognplot-port", default="12345", type=int)

    args = parser.parse_args()

    try:
        lnp_client = LognplotTcpClient(
            hostname=args.lognplot_hostname, port=args.lognplot_port
        )
        lnp_client.connect()
    except ConnectionError as e:
        lnp_client = None
        print("Lognplot connection error", e)

    ads_client = AdsClient(args.ams_net_id, args.ams_net_port, lnp_client)

    entries = ads_client.get_ads_entries()

    app = QApplication(sys.argv)

    model = TreeModel()
    model.populate(entries)

    filterModel = FilterModel()
    filterModel.setSourceModel(model)
    # filterModel.setFilterWildcard("GVL*")

    view = QTreeView()
    view.setModel(filterModel)

    def on_clicked(index):
        name = index.internalPointer().item_data()[1]
        typ = index.internalPointer().item_data()[2]
        print(name, typ)
        ads_client.subscribe_by_name(name, typ)

    view.doubleClicked.connect(on_clicked)

    view.setWindowTitle("Plc UiX")
    view.show()
    sys.exit(app.exec_())
