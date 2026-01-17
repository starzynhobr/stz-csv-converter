import QtQuick 2.15
import QtQuick.Controls 2.15

Button {
    id: control
    required property var theme
    property bool primary: false
    hoverEnabled: true
    property bool isHovered: hoverHandler.hovered || control.hovered

    leftPadding: 14
    rightPadding: 14
    implicitHeight: 36

    HoverHandler {
        id: hoverHandler
        acceptedDevices: PointerDevice.Mouse
        cursorShape: Qt.PointingHandCursor
        enabled: control.enabled
    }

    contentItem: Text {
        text: control.text
        font.pixelSize: 13
        font.bold: control.primary
        color: control.enabled
            ? (control.primary ? "#0b0e13" : (control.theme ? control.theme.text : "#e6edf3"))
            : (control.theme ? control.theme.subtext : "#8a93a4")
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        id: backgroundRect
        radius: 8
        color: control.enabled
            ? (control.primary ? (control.theme ? control.theme.accent : "#4ea1ff")
                               : (control.theme ? control.theme.surfaceAlt : "#161d26"))
            : (control.theme ? control.theme.surface : "#0f1319")
        border.color: control.enabled && control.isHovered
            ? (control.theme ? control.theme.accent : "#4ea1ff")
            : (control.theme ? control.theme.border : "#2a3644")
        border.width: 1

        Rectangle {
            anchors.fill: parent
            radius: backgroundRect.radius
            color: "#ffffff"
            opacity: control.down ? 0.18 : (control.isHovered ? 0.08 : 0.0)
        }
    }
}
