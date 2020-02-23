from lognplot.client import LognplotTcpClient
from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtCore import Qt
from TreeModel import TreeModel
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
    except ConnectionError:
        lnp_client = None
        print("Connection error")

    ads_client = AdsClient(args.ams_net_id, args.ams_net_port, lnp_client)

    entries = ads_client.get_ads_entries()
    # entries.append(
    #     AdsClient.VariableDescriptionEntry(
    #         "TEST.Var.Input", "LREAL", "This is an input", 0, 8
    #     )
    # )
    # entries.append(
    #     AdsClient.VariableDescriptionEntry(
    #         "TEST.Var.Output", "LREAL", "This is an output", 0, 8
    #     )
    # )

    app = QApplication(sys.argv)

    model = TreeModel()
    model.populate(entries)

    view = QTreeView()
    view.setModel(model)

    def on_clicked(index):
        name = index.internalPointer().item_data()[1]
        typ = index.internalPointer().item_data()[2]
        ads_client.subscribe_by_name(name, typ)

    view.doubleClicked.connect(on_clicked)

    view.setWindowTitle("PlcMagicUiX")
    view.show()
    sys.exit(app.exec_())
