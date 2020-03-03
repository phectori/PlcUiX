from lognplot.client import LognplotTcpClient
from PyQt5.QtCore import QUrl, QThread
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine
from ViewModels.ViewModel import ViewModel
from Models.AdsClient import AdsClient
import sys
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--ams-net-id", help="ams net id", default="127.0.0.1.1.1", type=str
    )
    parser.add_argument("--ams-net-port", help="ams net port", default=851, type=int)
    parser.add_argument(
        "--plc-hostname", help="ip address of the plc", default=None, type=str
    )
    parser.add_argument("--lognplot-hostname", default="localhost", type=str)
    parser.add_argument("--lognplot-port", default="12345", type=int)

    return parser.parse_args()


def init_lognplot(hostname, port):
    client = None
    try:
        client = LognplotTcpClient(hostname=hostname, port=port)
        print("Connecting to lognplot...")
        client.connect()
    except ConnectionError as err:
        print("Error while connecting to lognplot: ", err)
    except TimeoutError as err:
        print("Error while connecting to lognplot: ", err)

    return client


if __name__ == "__main__":
    args = parse_arguments()

    # Create lognplot client
    lnp_client = init_lognplot(args.lognplot_hostname, args.lognplot_port)

    # Create application
    app = QApplication(sys.argv)

    # Create a QML engine.
    engine = QQmlApplicationEngine()

    # Set a root context
    # https://codereview.stackexchange.com/questions/138992/simple-pyqt5-counting-gui
    ads_client = AdsClient(
        args.ams_net_id, args.ams_net_port, args.plc_hostname, lnp_client.send_sample
    )
    vm = ViewModel(ads_client)
    engine.rootContext().setContextProperty("vm", vm)

    # Create a component factory and load the QML script.
    engine.load(QUrl("QML/main.qml"))

    # Qml file error handling
    if not engine.rootObjects():
        print("Failed to find root object in QML")
        sys.exit(-1)

    engine.quit.connect(app.quit)

    sys.exit(app.exec_())
