import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "pages"
import "components"

ApplicationWindow {
    id: window
    width: 1200
    height: 820
    minimumWidth: 960
    minimumHeight: 640
    visible: true
    title: "CSV → Google Contacts"

    property int stepIndex: 0

    QtObject {
        id: theme
        property string fontFamily: "Segoe UI"
        property color background1: "#12161c"
        property color background2: "#0d1117"
        property color card: "#1a222c"
        property color border: "#2a3644"
        property color header: "#232e3a"
        property color surface: "#0f1319"
        property color surfaceAlt: "#161d26"
        property color rowOdd: "#141b24"
        property color rowEven: "#111821"
        property color text: "#e6edf3"
        property color subtext: "#a0acbb"
        property color accent: "#4ea1ff"
        property color accent2: "#3cc9a9"
        property color warning: "#f0b35a"
        property color danger: "#ff6b6b"
    }

    font.family: theme.fontFamily
    palette {
        window: theme.background2
        windowText: theme.text
        base: theme.surface
        text: theme.text
        button: theme.surfaceAlt
        buttonText: theme.text
        highlight: theme.accent
        highlightedText: "#0b0e13"
        placeholderText: theme.subtext
    }

    background: Rectangle {
        gradient: Gradient {
            GradientStop { position: 0.0; color: theme.background1 }
            GradientStop { position: 1.0; color: theme.background2 }
        }
        Rectangle {
            width: 280
            height: 280
            radius: 140
            color: "#253142"
            opacity: 0.35
            x: -60
            y: 80
        }
        Rectangle {
            width: 220
            height: 220
            radius: 110
            color: "#23323b"
            opacity: 0.3
            x: parent.width - 220
            y: parent.height - 260
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        Rectangle {
            Layout.fillWidth: true
            radius: 18
            color: theme.card
            border.color: theme.border
            border.width: 1
            implicitHeight: headerLayout.implicitHeight + 32

            RowLayout {
                id: headerLayout
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    Text {
                        text: "Conversor CSV → Google Contacts"
                        font.pixelSize: 24
                        font.bold: true
                        color: theme.text
                    }
                    Text {
                        text: "Pipeline seguro com dedupe e batches"
                        font.pixelSize: 13
                        color: theme.subtext
                    }
                }

                RowLayout {
                    spacing: 8
                    Repeater {
                        model: ["Importar", "Regras", "Execução", "Resultado"]
                        delegate: Rectangle {
                            radius: 12
                            color: index === stepIndex ? theme.accent : theme.surfaceAlt
                            border.color: theme.border
                            border.width: 1
                            width: 90
                            height: 32

                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                font.pixelSize: 12
                                font.bold: index === stepIndex
                                color: index === stepIndex ? "#0b0e13" : theme.text
                            }
                        }
                    }
                }
            }
        }

        StackLayout {
            id: stack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: stepIndex

            ImportPage {
                theme: theme
                enabled: !controller.busy
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            RulesPage {
                theme: theme
                enabled: !controller.busy
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            RunPage {
                theme: theme
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            ResultsPage {
                theme: theme
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 16
            color: theme.card
            border.color: theme.border
            border.width: 1
            implicitHeight: footerLayout.implicitHeight + 24

            RowLayout {
                id: footerLayout
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                AppButton {
                    theme: theme
                    text: "Voltar"
                    enabled: stepIndex > 0 && !controller.busy
                    onClicked: stepIndex = Math.max(0, stepIndex - 1)
                }
                AppButton {
                    theme: theme
                    primary: true
                    text: stepIndex < 3 ? "Próximo" : "Final"
                    enabled: stepIndex < 3 && !controller.busy
                    onClicked: stepIndex = Math.min(3, stepIndex + 1)
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: controller.busy ? "Processando..." : "Pronto"
                    color: controller.busy ? theme.accent2 : theme.subtext
                }
            }
        }
    }
}
