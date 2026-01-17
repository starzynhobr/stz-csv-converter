import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: card
    property string title: ""
    property string value: ""
    required property var theme
    property color accentColor: "#4ea1ff"
    radius: 14
    color: theme ? theme.card : "#1a222c"
    border.color: theme ? theme.border : "#2a3644"
    border.width: 1
    implicitWidth: 200
    implicitHeight: 110

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 6

        Text {
            text: card.title
            font.pixelSize: 13
            color: theme ? theme.subtext : "#a0acbb"
            elide: Text.ElideRight
        }

        Text {
            text: card.value
            font.pixelSize: 26
            font.bold: true
            color: card.accentColor
            elide: Text.ElideRight
        }
    }
}
