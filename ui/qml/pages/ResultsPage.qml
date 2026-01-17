import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"

Item {
    id: page
    required property var theme

    function reasonLabel(code) {
        if (code === "phone_length") {
            return "Telefone curto/longo"
        }
        if (code === "name_mojibake") {
            return "Nome com mojibake"
        }
        return code
    }

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
                implicitHeight: resultsLayout.implicitHeight + 32

                ColumnLayout {
                    id: resultsLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Resultado"
                        font.pixelSize: 20
                        font.bold: true
                        color: theme.text
                    }

                    Flow {
                        width: parent.width
                        spacing: 12

                        StatCard {
                            title: "Lidos"
                            value: controller.reportCounts["total_rows"] !== undefined ? controller.reportCounts["total_rows"] : "-"
                            accentColor: theme ? theme.accent : "#4ea1ff"
                            theme: theme
                        }
                        StatCard {
                            title: "Sem telefone"
                            value: controller.reportCounts["without_phone"] !== undefined ? controller.reportCounts["without_phone"] : "-"
                            accentColor: theme ? theme.warning : "#f0b35a"
                            theme: theme
                        }
                        StatCard {
                            title: "Duplicados fundidos"
                            value: controller.reportCounts["duplicates_merged"] !== undefined ? controller.reportCounts["duplicates_merged"] : "-"
                            accentColor: theme ? theme.accent2 : "#3cc9a9"
                            theme: theme
                        }
                        StatCard {
                            title: "Contatos explodidos"
                            value: controller.reportCounts["contacts_exploded_total"] !== undefined ? controller.reportCounts["contacts_exploded_total"] : "-"
                            accentColor: theme ? theme.accent : "#4ea1ff"
                            theme: theme
                        }
                        StatCard {
                            title: "Suspeitos"
                            value: controller.reportCounts["suspects"] !== undefined ? controller.reportCounts["suspects"] : "-"
                            accentColor: theme ? theme.danger : "#ff6b6b"
                            theme: theme
                        }
                        StatCard {
                            title: "Arquivos gerados"
                            value: controller.reportCounts["output_files"] !== undefined ? controller.reportCounts["output_files"] : "-"
                            accentColor: theme ? theme.accent : "#4ea1ff"
                            theme: theme
                        }
                    }

                    ColumnLayout {
                        spacing: 6
                        Repeater {
                            model: controller.reportWarnings
                            Text {
                                text: "Aviso: " + modelData
                                color: theme.warning
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        AppButton {
                            theme: theme
                            text: "Abrir pasta de saída"
                            enabled: controller.reportOutputs.length > 0
                            onClicked: controller.openOutputDir()
                        }
                        AppButton {
                            theme: theme
                            text: "Abrir report.json"
                            enabled: controller.reportPath.length > 0
                            onClicked: controller.openReport()
                        }
                        AppButton {
                            theme: theme
                            primary: true
                            text: "Copiar resumo"
                            enabled: controller.summaryText.length > 0
                            onClicked: controller.copySummary()
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: theme.card
                border.color: theme.border
                border.width: 1
                implicitHeight: suspectLayout.implicitHeight + 32

                ColumnLayout {
                    id: suspectLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    Text {
                        text: "Suspeitos"
                        font.pixelSize: 18
                        font.bold: true
                        color: theme.text
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 260
                        radius: 10
                        color: theme.surface
                        border.color: theme.border
                        border.width: 1
                        clip: true

                        ColumnLayout {
                            anchors.fill: parent
                            spacing: 4

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.preferredHeight: 28
                                    color: theme.header
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 12
                                        Text { text: "Motivo"; color: theme.text; width: 160 }
                                        Text { text: "Fonte"; color: theme.text; width: 80 }
                                        Text { text: "Telefone original"; color: theme.text; width: 180 }
                                        Text { text: "Telefone normalizado"; color: theme.text; width: 180 }
                                        Text { text: "Nome"; color: theme.text; width: 160 }
                                        Text { text: "Sugestão"; color: theme.text; width: 200 }
                                        Text { text: "Linha"; color: theme.text; width: 60 }
                                    }
                                }
                            }

                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                model: controller.suspectsModel
                                clip: true
                                delegate: Rectangle {
                                    width: ListView.view ? ListView.view.width : parent.width
                                    Layout.fillWidth: true
                                    height: 28
                                    color: index % 2 === 0 ? theme.rowEven : theme.rowOdd
                                    RowLayout {
                                        anchors.fill: parent
                                        anchors.margins: 6
                                        spacing: 12
                                        Text { text: reasonLabel(reason); color: theme.text; width: 160; elide: Text.ElideRight }
                                        Text { text: source; color: theme.subtext; width: 80 }
                                        Text { text: raw_phone; color: theme.subtext; width: 180; elide: Text.ElideRight }
                                        Text { text: normalized_phone; color: theme.subtext; width: 180; elide: Text.ElideRight }
                                        Text { text: name; color: theme.subtext; width: 160; elide: Text.ElideRight }
                                        Text { text: suggested_fix; color: theme.subtext; width: 200; elide: Text.ElideRight }
                                        Text { text: line; color: theme.subtext; width: 60 }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
