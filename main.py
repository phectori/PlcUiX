from PyQt5.QtWidgets import QApplication, QTreeView
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
    args = parser.parse_args()

    ads_client = AdsClient(args.ams_net_id, args.ams_net_port)

    entries = ads_client.get_ads_entries()
    entries.append(AdsClient.VariableDescriptionEntry("TEST.Var.Input", "LREAL", "This is an input", 0, 8))
    entries.append(AdsClient.VariableDescriptionEntry("TEST.Var.Output", "LREAL", "This is an output", 0, 8))

    app = QApplication(sys.argv)

    model = TreeModel()
    model.populate(entries)

    view = QTreeView()
    view.setModel(model)
    view.setWindowTitle("PlcMagicUiX")
    view.show()
    sys.exit(app.exec_())
