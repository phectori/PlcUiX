import FilterModel 1.0
import QtQuick.Controls 1.4
import QtQuick.Window 2.2
import QtQuick 2.3

Window {
    visible: true
    title: vm.name
    width: 800
    height: 600

    TreeView {
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
        anchors.fill: parent
        model: vm.model
    }
}
