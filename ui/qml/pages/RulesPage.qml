import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

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
                implicitHeight: configLayout.implicitHeight + 32

                ColumnLayout {
                    id: configLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: "Regras e configurações"
                        font.pixelSize: 20
                        font.bold: true
                        color: theme.text
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: width > 760 ? 3 : 1
                        columnSpacing: 16
                        rowSpacing: 12

                        ColumnLayout {
                            spacing: 6
                            Text { text: "DDI default"; color: theme.subtext }
                            TextField {
                                text: controller.ddiDefault
                                enabled: !controller.busy
                                inputMethodHints: Qt.ImhDigitsOnly
                                validator: IntValidator { bottom: 1 }
                                onEditingFinished: controller.ddiDefault = text
                            }
                        }

                        ColumnLayout {
                            spacing: 6
                            Text { text: "Batch size"; color: theme.subtext }
                            TextField {
                                text: String(controller.batchSize)
                                enabled: !controller.busy
                                inputMethodHints: Qt.ImhDigitsOnly
                                validator: IntValidator { bottom: 1 }
                                onEditingFinished: if (text.length > 0) controller.batchSize = parseInt(text)
                            }
                        }

                        ColumnLayout {
                            spacing: 6
                            Text { text: "Label"; color: theme.subtext }
                            TextField {
                                text: controller.label
                                enabled: !controller.busy
                                onEditingFinished: controller.label = text
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        ColumnLayout {
                            spacing: 6
                            Text { text: "Formato do telefone"; color: theme.subtext }
                            RowLayout {
                                spacing: 12
                                RadioButton {
                                    text: "55..."
                                    checked: !controller.phonePrefixPlus
                                    enabled: !controller.busy
                                    onToggled: if (checked) controller.phonePrefixPlus = false
                                }
                                RadioButton {
                                    text: "+55..."
                                    checked: controller.phonePrefixPlus
                                    enabled: !controller.busy
                                    onToggled: if (checked) controller.phonePrefixPlus = true
                                }
                            }
                        }

                        ColumnLayout {
                            spacing: 6
                            Text { text: "Min len"; color: theme.subtext }
                            TextField {
                                text: String(controller.minPhoneLen)
                                enabled: !controller.busy
                                inputMethodHints: Qt.ImhDigitsOnly
                                validator: IntValidator { bottom: 1 }
                                onEditingFinished: if (text.length > 0) controller.minPhoneLen = parseInt(text)
                            }
                        }

                        ColumnLayout {
                            spacing: 6
                            Text { text: "Max len"; color: theme.subtext }
                            TextField {
                                text: String(controller.maxPhoneLen)
                                enabled: !controller.busy
                                inputMethodHints: Qt.ImhDigitsOnly
                                validator: IntValidator { bottom: 1 }
                                onEditingFinished: if (text.length > 0) controller.maxPhoneLen = parseInt(text)
                            }
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
                implicitHeight: mergeLayout.implicitHeight + 32

                ColumnLayout {
                    id: mergeLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Regras de merge"
                        font.pixelSize: 18
                        font.bold: true
                        color: theme.text
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 24
                        CheckBox {
                            text: "Dedupe por telefone"
                            checked: controller.dedupeEnabled
                            enabled: !controller.busy
                            onToggled: controller.dedupeEnabled = checked
                        }
                        CheckBox {
                            text: "Renomear contatos com nome numérico"
                            checked: controller.renamePhoneLikeNames
                            enabled: !controller.busy
                            onToggled: controller.renamePhoneLikeNames = checked
                        }
                        CheckBox {
                            text: "Não sobrescrever nome bom por vazio"
                            checked: controller.protectGoodName
                            enabled: !controller.busy
                            onToggled: controller.protectGoodName = checked
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 24
                        CheckBox {
                            text: "Explodir múltiplos telefones"
                            checked: controller.explodePhones
                            enabled: !controller.busy
                            onToggled: controller.explodePhones = checked
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        Text {
                            text: "Prefixo do fallback"
                            color: theme.subtext
                        }
                        TextField {
                            Layout.preferredWidth: 220
                            text: controller.fallbackPrefix
                            enabled: !controller.busy
                            placeholderText: "Cliente"
                            onEditingFinished: controller.fallbackPrefix = text
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
                implicitHeight: overrideLayout.implicitHeight + 32

                ColumnLayout {
                    id: overrideLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Overrides de colunas (opcional)"
                        font.pixelSize: 18
                        font.bold: true
                        color: theme.text
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: width > 760 ? 3 : 1
                        columnSpacing: 16
                        rowSpacing: 12

                        ColumnLayout {
                            spacing: 6
                            Text { text: "Nome"; color: theme.subtext }
                            TextField {
                                text: controller.colName
                                enabled: !controller.busy
                                onEditingFinished: controller.colName = text
                            }
                        }
                        ColumnLayout {
                            spacing: 6
                            Text { text: "Telefone"; color: theme.subtext }
                            TextField {
                                text: controller.colPhone
                                enabled: !controller.busy
                                onEditingFinished: controller.colPhone = text
                            }
                        }
                        ColumnLayout {
                            spacing: 6
                            Text { text: "DDI"; color: theme.subtext }
                            TextField {
                                text: controller.colDdi
                                enabled: !controller.busy
                                onEditingFinished: controller.colDdi = text
                            }
                        }
                        ColumnLayout {
                            spacing: 6
                            Text { text: "Tags"; color: theme.subtext }
                            TextField {
                                text: controller.colTags
                                enabled: !controller.busy
                                onEditingFinished: controller.colTags = text
                            }
                        }
                        ColumnLayout {
                            spacing: 6
                            Text { text: "Criado em"; color: theme.subtext }
                            TextField {
                                text: controller.colCreated
                                enabled: !controller.busy
                                onEditingFinished: controller.colCreated = text
                            }
                        }
                        ColumnLayout {
                            spacing: 6
                            Text { text: "Notas"; color: theme.subtext }
                            TextField {
                                text: controller.colNotes
                                enabled: !controller.busy
                                onEditingFinished: controller.colNotes = text
                            }
                        }
                        ColumnLayout {
                            spacing: 6
                            Text { text: "Labels"; color: theme.subtext }
                            TextField {
                                text: controller.colLabels
                                enabled: !controller.busy
                                onEditingFinished: controller.colLabels = text
                            }
                        }
                    }
                }
            }
        }
    }
}
