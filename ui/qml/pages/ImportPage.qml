import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs
import "../components"

Item {
    id: page
    required property var theme
    property int colDdiWidth: 70
    property int colPhoneWidth: 160
    property int colTagsWidth: 160
    property int colCreatedWidth: 140

    function valueOrDash(value) {
        return value === undefined || value === null || value === "" ? "-" : value
    }

    function formatColumns(columns) {
        if (!columns) {
            return "-"
        }
        var parts = []
        for (var key in columns) {
            if (columns[key]) {
                parts.push(key + ": " + columns[key])
            }
        }
        return parts.length > 0 ? parts.join(", ") : "-"
    }

    FileDialog {
        id: crmDialog
        title: "Selecionar CSV do CRM"
        nameFilters: ["CSV (*.csv)"]
        onAccepted: controller.setCrmPathFromUrl(selectedFile)
    }

    FileDialog {
        id: googleDialog
        title: "Selecionar CSV do Google (opcional)"
        nameFilters: ["CSV (*.csv)"]
        onAccepted: controller.setGooglePathFromUrl(selectedFile)
    }

    FolderDialog {
        id: outDialog
        title: "Selecionar pasta de saída"
        onAccepted: controller.setOutDirFromUrl(selectedFolder)
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
                implicitHeight: importLayout.implicitHeight + 32

                ColumnLayout {
                    id: importLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: "Importação"
                        font.pixelSize: 20
                        font.bold: true
                        color: theme.text
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        AppButton {
                            theme: theme
                            text: "Selecionar CSV do CRM..."
                            enabled: !controller.busy
                            onClicked: crmDialog.open()
                        }
                        TextField {
                            Layout.fillWidth: true
                            readOnly: true
                            text: controller.crmPath
                            placeholderText: "Nenhum arquivo selecionado"
                        }
                        AppButton {
                            theme: theme
                            text: "Remover"
                            enabled: !controller.busy && controller.crmPath.length > 0
                            Layout.preferredWidth: 90
                            onClicked: controller.clearCrmPath()
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        AppButton {
                            theme: theme
                            text: "Selecionar CSV do Google (opcional)..."
                            enabled: !controller.busy
                            onClicked: googleDialog.open()
                        }
                        TextField {
                            Layout.fillWidth: true
                            readOnly: true
                            text: controller.googlePath
                            placeholderText: "Nenhum arquivo selecionado"
                        }
                        AppButton {
                            theme: theme
                            text: "Remover"
                            enabled: !controller.busy && controller.googlePath.length > 0
                            Layout.preferredWidth: 90
                            onClicked: controller.clearGooglePath()
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        AppButton {
                            theme: theme
                            text: "Selecionar pasta de saída..."
                            enabled: !controller.busy
                            onClicked: outDialog.open()
                        }
                        TextField {
                            Layout.fillWidth: true
                            readOnly: true
                            text: controller.outDir
                            placeholderText: "Nenhuma pasta selecionada"
                        }
                        AppButton {
                            theme: theme
                            text: "Remover"
                            enabled: !controller.busy && controller.outDir.length > 0
                            Layout.preferredWidth: 90
                            onClicked: controller.clearOutDir()
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        AppButton {
                            theme: theme
                            primary: true
                            text: "Validar / Auto-detectar"
                            enabled: !controller.busy
                            onClicked: controller.validateInputs()
                        }
                        Text {
                            text: controller.status
                            color: theme.subtext
                            elide: Text.ElideRight
                            Layout.fillWidth: true
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
                implicitHeight: diagnosticLayout.implicitHeight + 32

                ColumnLayout {
                    id: diagnosticLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Diagnóstico"
                        font.pixelSize: 18
                        font.bold: true
                        color: theme.text
                    }

                    Text {
                        text: controller.validationError
                        color: theme.danger
                        visible: controller.validationError.length > 0
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text { text: "CRM"; font.bold: true; color: theme.text }
                            Text {
                                text: "Encoding: " + valueOrDash(controller.validationResult["crm"] ? controller.validationResult["crm"]["encoding"] : "")
                                color: theme.subtext
                            }
                            Text {
                                text: "Delimitador: " + valueOrDash(controller.validationResult["crm"] ? controller.validationResult["crm"]["delimiter"] : "")
                                color: theme.subtext
                            }
                            Text {
                                text: "Linhas (aprox): " + valueOrDash(controller.validationResult["crm_line_count"])
                                color: theme.subtext
                            }
                            Text {
                                text: "Sem telefone (aprox): " + valueOrDash(controller.validationResult["crm_without_phone"])
                                color: theme.subtext
                            }
                            Text {
                                text: "Duplicados (aprox): " + valueOrDash(controller.validationResult["crm_duplicates"])
                                color: theme.subtext
                            }
                            Text {
                                text: "Fallback encoding: " + valueOrDash(controller.validationResult["crm"] ? controller.validationResult["crm"]["used_fallback"] : "")
                                color: theme.subtext
                            }
                            Text {
                                text: "Colunas: " + formatColumns(controller.validationResult["crm"] ? controller.validationResult["crm"]["columns"] : null)
                                color: theme.subtext
                                wrapMode: Text.Wrap
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text { text: "Google"; font.bold: true; color: theme.text }
                            Text {
                                text: "Encoding: " + valueOrDash(controller.validationResult["google"] ? controller.validationResult["google"]["encoding"] : "")
                                color: theme.subtext
                            }
                            Text {
                                text: "Delimitador: " + valueOrDash(controller.validationResult["google"] ? controller.validationResult["google"]["delimiter"] : "")
                                color: theme.subtext
                            }
                            Text {
                                text: "Linhas (aprox): " + valueOrDash(controller.validationResult["google_line_count"])
                                color: theme.subtext
                            }
                            Text {
                                text: "Sem telefone (aprox): " + valueOrDash(controller.validationResult["google_without_phone"])
                                color: theme.subtext
                            }
                            Text {
                                text: "Duplicados (aprox): " + valueOrDash(controller.validationResult["google_duplicates"])
                                color: theme.subtext
                            }
                            Text {
                                text: "Fallback encoding: " + valueOrDash(controller.validationResult["google"] ? controller.validationResult["google"]["used_fallback"] : "")
                                color: theme.subtext
                            }
                            Text {
                                text: "Colunas: " + formatColumns(controller.validationResult["google"] ? controller.validationResult["google"]["columns"] : null)
                                color: theme.subtext
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    Text {
                        text: controller.previewHasMojibake ? "Aviso: caracteres suspeitos detectados na prévia." : ""
                        color: theme.warning
                        visible: controller.previewHasMojibake
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                radius: 16
                color: theme.card
                border.color: theme.border
                border.width: 1
                implicitHeight: previewLayout.implicitHeight + 32

                ColumnLayout {
                    id: previewLayout
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    Text {
                        text: "Prévia (até 50 linhas)"
                        font.pixelSize: 18
                        font.bold: true
                        color: theme.text
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 240
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
                                        Text {
                                            text: "Nome"
                                            color: theme.text
                                            Layout.fillWidth: true
                                            Layout.minimumWidth: 200
                                            elide: Text.ElideRight
                                        }
                                        Text { text: "DDI"; color: theme.text; Layout.preferredWidth: colDdiWidth }
                                        Text { text: "Telefone"; color: theme.text; Layout.preferredWidth: colPhoneWidth }
                                        Text { text: "Tags"; color: theme.text; Layout.preferredWidth: colTagsWidth }
                                        Text { text: "Criado em"; color: theme.text; Layout.preferredWidth: colCreatedWidth }
                                    }
                                }
                            }

                            ListView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                model: controller.previewModel
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
                                        Text {
                                            text: name
                                            color: theme.text
                                            Layout.fillWidth: true
                                            Layout.minimumWidth: 200
                                            elide: Text.ElideRight
                                        }
                                        Text { text: ddi; color: theme.subtext; Layout.preferredWidth: colDdiWidth; elide: Text.ElideRight }
                                        Text { text: phone; color: theme.subtext; Layout.preferredWidth: colPhoneWidth; elide: Text.ElideRight }
                                        Text { text: tags; color: theme.subtext; Layout.preferredWidth: colTagsWidth; elide: Text.ElideRight }
                                        Text { text: created; color: theme.subtext; Layout.preferredWidth: colCreatedWidth; elide: Text.ElideRight }
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
