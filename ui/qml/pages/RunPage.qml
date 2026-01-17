import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"

Item {
    id: page
    required property var theme

    ScrollView {
        anchors.fill: parent
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 18

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: theme.card
                border.color: theme.border
                border.width: 1
                implicitHeight: runLayout.implicitHeight + 32

                ColumnLayout {
                    id: runLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: "Execução"
                        font.pixelSize: 20
                        font.bold: true
                        color: theme.text
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        AppButton {
                            theme: theme
                            text: "Dry-run (só relatório)"
                            enabled: !controller.busy
                            onClicked: controller.startDryRun()
                        }
                        AppButton {
                            theme: theme
                            primary: true
                            text: "Gerar CSVs"
                            enabled: !controller.busy
                            onClicked: controller.startRun()
                        }
                        AppButton {
                            theme: theme
                            text: "Cancelar"
                            enabled: controller.busy
                            onClicked: controller.cancelRun()
                        }
                    }

                    ProgressBar {
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        value: controller.progress
                    }

                    Text {
                        text: controller.status
                        color: theme.subtext
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: theme.card
                border.color: theme.border
                border.width: 1
                implicitHeight: logLayout.implicitHeight + 32

                ColumnLayout {
                    id: logLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    Text {
                        text: "Logs"
                        font.pixelSize: 18
                        font.bold: true
                        color: theme.text
                    }

                    TextArea {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 260
                        text: controller.logText
                        readOnly: true
                        wrapMode: TextArea.Wrap
                        color: theme.text
                        selectionColor: theme.accent
                        selectedTextColor: "#0b0e13"
                        background: Rectangle {
                            color: theme.surface
                            border.color: theme.border
                            border.width: 1
                            radius: 8
                        }
                    }
                }
            }
        }
    }
}
