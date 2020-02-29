import FilterModel 1.0
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick 2.3
import QtQuick.Layouts 1.14

Window {
    visible: true
    title: vm.name
    width: 800
    height: 600

    Component.onCompleted: {
        adsEntriesTreeView.doubleClicked.connect(vm.on_double_clicked)
    }

    GridLayout {
        anchors.fill: parent
        columns: 1
        rows: 2

        TextField {
            id: searchField
            Layout.fillWidth: true
            Layout.margins: 5
            placeholderText: qsTr("Enter filter")
            onTextChanged: vm.model.setFilterRegExp(text)
        }

        TreeView {
            id: adsEntriesTreeView
            Layout.fillWidth: true
            TableViewColumn {
                title: "Name"
                role: "name"
                width: 300
            }
            TableViewColumn {
                title: "Type"
                role: "type"
                width: 100
            }
            TableViewColumn {
                title: "Size"
                role: "size"
                width: 100
            }
            TableViewColumn {
                title: "Comment"
                role: "comment"
                width: 200
            }
            model: vm.model
            Layout.fillHeight: true
        }
    }
}
