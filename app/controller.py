from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Property, QThread, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QGuiApplication

from app.models import PreviewModel, SuspectModel
from app.worker import PipelineWorker, ValidationWorker
from core.config import ColumnOverrides, Config


class Controller(QObject):
    pathsChanged = Signal()
    configChanged = Signal()
    overridesChanged = Signal()
    stateChanged = Signal()
    logChanged = Signal()
    validationChanged = Signal()
    reportChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._crm_path = ""
        self._google_path = ""
        self._out_dir = ""

        self._ddi_default = "55"
        self._batch_size = 3000
        self._label = "CRM_2025"
        self._phone_prefix_plus = False
        self._min_phone_len = 12
        self._max_phone_len = 13
        self._dedupe_enabled = True
        self._protect_good_name = True
        self._rename_phone_like_names = True
        self._explode_phones = True
        self._fallback_prefix = "Cliente"

        self._col_name = ""
        self._col_phone = ""
        self._col_ddi = ""
        self._col_tags = ""
        self._col_created = ""
        self._col_notes = ""
        self._col_labels = ""

        self._busy = False
        self._progress = 0
        self._status = ""
        self._log_lines: list[str] = []

        self._validation_result: dict[str, Any] = {}
        self._validation_error = ""
        self._preview_has_mojibake = False

        self._report_counts: dict[str, Any] = {}
        self._report_warnings: list[str] = []
        self._report_outputs: list[str] = []
        self._report_path = ""
        self._summary_text = ""

        self._preview_model = PreviewModel()
        self._suspects_model = SuspectModel()

        self._worker_thread: QThread | None = None
        self._worker: PipelineWorker | None = None

        self._validation_thread: QThread | None = None
        self._validation_worker: ValidationWorker | None = None

    def _set_attr(self, name: str, value: Any, signal: Signal) -> None:
        if getattr(self, name) == value:
            return
        setattr(self, name, value)
        signal.emit()

    def _append_log(self, message: str) -> None:
        if not message:
            return
        self._log_lines.append(message)
        if len(self._log_lines) > 200:
            self._log_lines = self._log_lines[-200:]
        self.logChanged.emit()

    def _build_config(self) -> Config:
        return Config(
            ddi_default=self._ddi_default or "55",
            assume_ddi=True,
            batch_size=int(self._batch_size),
            label=self._label,
            phone_prefix_plus=self._phone_prefix_plus,
            min_phone_len=int(self._min_phone_len),
            max_phone_len=int(self._max_phone_len),
            dedupe_enabled=self._dedupe_enabled,
            treat_dot_as_empty=True,
            protect_good_name=self._protect_good_name,
            rename_phone_like_names=self._rename_phone_like_names,
            explode_phones=self._explode_phones,
            fallback_prefix=self._fallback_prefix,
        )

    def _build_overrides(self) -> ColumnOverrides:
        return ColumnOverrides(
            name=self._col_name or None,
            phone=self._col_phone or None,
            ddi=self._col_ddi or None,
            tags=self._col_tags or None,
            created=self._col_created or None,
            notes=self._col_notes or None,
            labels=self._col_labels or None,
        )

    def _set_busy(self, value: bool) -> None:
        self._set_attr("_busy", value, self.stateChanged)

    def _set_status(self, value: str) -> None:
        self._set_attr("_status", value, self.stateChanged)

    def _reset_report(self) -> None:
        self._report_counts = {}
        self._report_warnings = []
        self._report_outputs = []
        self._report_path = ""
        self._summary_text = ""
        self._suspects_model.clear()
        self.reportChanged.emit()

    @Property(str, notify=pathsChanged)
    def crmPath(self) -> str:
        return self._crm_path

    @crmPath.setter
    def crmPath(self, value: str) -> None:
        self._set_attr("_crm_path", value, self.pathsChanged)

    @Property(str, notify=pathsChanged)
    def googlePath(self) -> str:
        return self._google_path

    @googlePath.setter
    def googlePath(self, value: str) -> None:
        self._set_attr("_google_path", value, self.pathsChanged)

    @Property(str, notify=pathsChanged)
    def outDir(self) -> str:
        return self._out_dir

    @outDir.setter
    def outDir(self, value: str) -> None:
        self._set_attr("_out_dir", value, self.pathsChanged)

    @Property(str, notify=configChanged)
    def ddiDefault(self) -> str:
        return self._ddi_default

    @ddiDefault.setter
    def ddiDefault(self, value: str) -> None:
        self._set_attr("_ddi_default", value, self.configChanged)

    @Property(int, notify=configChanged)
    def batchSize(self) -> int:
        return self._batch_size

    @batchSize.setter
    def batchSize(self, value: int) -> None:
        self._set_attr("_batch_size", value, self.configChanged)

    @Property(str, notify=configChanged)
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._set_attr("_label", value, self.configChanged)

    @Property(bool, notify=configChanged)
    def phonePrefixPlus(self) -> bool:
        return self._phone_prefix_plus

    @phonePrefixPlus.setter
    def phonePrefixPlus(self, value: bool) -> None:
        self._set_attr("_phone_prefix_plus", value, self.configChanged)

    @Property(int, notify=configChanged)
    def minPhoneLen(self) -> int:
        return self._min_phone_len

    @minPhoneLen.setter
    def minPhoneLen(self, value: int) -> None:
        self._set_attr("_min_phone_len", value, self.configChanged)

    @Property(int, notify=configChanged)
    def maxPhoneLen(self) -> int:
        return self._max_phone_len

    @maxPhoneLen.setter
    def maxPhoneLen(self, value: int) -> None:
        self._set_attr("_max_phone_len", value, self.configChanged)

    @Property(bool, notify=configChanged)
    def dedupeEnabled(self) -> bool:
        return self._dedupe_enabled

    @dedupeEnabled.setter
    def dedupeEnabled(self, value: bool) -> None:
        self._set_attr("_dedupe_enabled", value, self.configChanged)

    @Property(bool, notify=configChanged)
    def renamePhoneLikeNames(self) -> bool:
        return self._rename_phone_like_names

    @renamePhoneLikeNames.setter
    def renamePhoneLikeNames(self, value: bool) -> None:
        self._set_attr("_rename_phone_like_names", value, self.configChanged)

    @Property(bool, notify=configChanged)
    def explodePhones(self) -> bool:
        return self._explode_phones

    @explodePhones.setter
    def explodePhones(self, value: bool) -> None:
        self._set_attr("_explode_phones", value, self.configChanged)

    @Property(str, notify=configChanged)
    def fallbackPrefix(self) -> str:
        return self._fallback_prefix

    @fallbackPrefix.setter
    def fallbackPrefix(self, value: str) -> None:
        self._set_attr("_fallback_prefix", value, self.configChanged)

    @Property(bool, notify=configChanged)
    def protectGoodName(self) -> bool:
        return self._protect_good_name

    @protectGoodName.setter
    def protectGoodName(self, value: bool) -> None:
        self._set_attr("_protect_good_name", value, self.configChanged)

    @Property(str, notify=overridesChanged)
    def colName(self) -> str:
        return self._col_name

    @colName.setter
    def colName(self, value: str) -> None:
        self._set_attr("_col_name", value, self.overridesChanged)

    @Property(str, notify=overridesChanged)
    def colPhone(self) -> str:
        return self._col_phone

    @colPhone.setter
    def colPhone(self, value: str) -> None:
        self._set_attr("_col_phone", value, self.overridesChanged)

    @Property(str, notify=overridesChanged)
    def colDdi(self) -> str:
        return self._col_ddi

    @colDdi.setter
    def colDdi(self, value: str) -> None:
        self._set_attr("_col_ddi", value, self.overridesChanged)

    @Property(str, notify=overridesChanged)
    def colTags(self) -> str:
        return self._col_tags

    @colTags.setter
    def colTags(self, value: str) -> None:
        self._set_attr("_col_tags", value, self.overridesChanged)

    @Property(str, notify=overridesChanged)
    def colCreated(self) -> str:
        return self._col_created

    @colCreated.setter
    def colCreated(self, value: str) -> None:
        self._set_attr("_col_created", value, self.overridesChanged)

    @Property(str, notify=overridesChanged)
    def colNotes(self) -> str:
        return self._col_notes

    @colNotes.setter
    def colNotes(self, value: str) -> None:
        self._set_attr("_col_notes", value, self.overridesChanged)

    @Property(str, notify=overridesChanged)
    def colLabels(self) -> str:
        return self._col_labels

    @colLabels.setter
    def colLabels(self, value: str) -> None:
        self._set_attr("_col_labels", value, self.overridesChanged)

    @Property(bool, notify=stateChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(int, notify=stateChanged)
    def progress(self) -> int:
        return self._progress

    @Property(str, notify=stateChanged)
    def status(self) -> str:
        return self._status

    @Property(str, notify=logChanged)
    def logText(self) -> str:
        return "\n".join(self._log_lines)

    @Property("QVariantMap", notify=validationChanged)
    def validationResult(self) -> dict[str, Any]:
        return self._validation_result

    @Property(str, notify=validationChanged)
    def validationError(self) -> str:
        return self._validation_error

    @Property(bool, notify=validationChanged)
    def previewHasMojibake(self) -> bool:
        return self._preview_has_mojibake

    @Property(QObject, constant=True)
    def previewModel(self) -> QObject:
        return self._preview_model

    @Property(QObject, constant=True)
    def suspectsModel(self) -> QObject:
        return self._suspects_model

    @Property("QVariantMap", notify=reportChanged)
    def reportCounts(self) -> dict[str, Any]:
        return self._report_counts

    @Property("QVariantList", notify=reportChanged)
    def reportWarnings(self) -> list[str]:
        return self._report_warnings

    @Property("QVariantList", notify=reportChanged)
    def reportOutputs(self) -> list[str]:
        return self._report_outputs

    @Property(str, notify=reportChanged)
    def reportPath(self) -> str:
        return self._report_path

    @Property(str, notify=reportChanged)
    def summaryText(self) -> str:
        return self._summary_text

    @Slot()
    def validateInputs(self) -> None:
        if self._busy:
            return
        if not self._crm_path and not self._google_path:
            self._validation_error = "Selecione o CSV do CRM ou do Google."
            self._validation_result = {}
            self._preview_model.clear()
            self.validationChanged.emit()
            return
        self._validation_error = ""
        self._validation_result = {}
        self._preview_has_mojibake = False
        self._preview_model.clear()
        self.validationChanged.emit()

        config = self._build_config()
        overrides = self._build_overrides()
        self._set_status("Validando entradas...")

        self._validation_thread = QThread()
        self._validation_worker = ValidationWorker(
            crm_path=self._crm_path or None,
            google_path=self._google_path or None,
            config=config,
            overrides=overrides,
            preview_limit=50,
            fast_scan_limit_bytes=5_000_000,
        )
        self._validation_worker.moveToThread(self._validation_thread)
        self._validation_thread.started.connect(self._validation_worker.run)
        self._validation_worker.finished.connect(self._on_validation_finished)
        self._validation_worker.error.connect(self._on_validation_error)
        self._validation_worker.finished.connect(self._validation_thread.quit)
        self._validation_worker.finished.connect(self._validation_worker.deleteLater)
        self._validation_thread.finished.connect(self._validation_thread.deleteLater)
        self._validation_thread.start()

    @Slot(QUrl)
    def setCrmPathFromUrl(self, url: QUrl) -> None:
        self.crmPath = url.toLocalFile()

    @Slot()
    def clearCrmPath(self) -> None:
        self.crmPath = ""
        self._reset_validation()

    @Slot(QUrl)
    def setGooglePathFromUrl(self, url: QUrl) -> None:
        self.googlePath = url.toLocalFile()

    @Slot()
    def clearGooglePath(self) -> None:
        self.googlePath = ""
        self._reset_validation()

    @Slot(QUrl)
    def setOutDirFromUrl(self, url: QUrl) -> None:
        self.outDir = url.toLocalFile()

    @Slot()
    def clearOutDir(self) -> None:
        self.outDir = ""

    @Slot()
    def startDryRun(self) -> None:
        self._start_pipeline(dry_run=True)

    @Slot()
    def startRun(self) -> None:
        self._start_pipeline(dry_run=False)

    def _start_pipeline(self, dry_run: bool) -> None:
        if self._busy:
            return
        if not self._crm_path and not self._google_path:
            self._set_status("Selecione CSV do CRM ou do Google e pasta de saída.")
            return
        if not self._out_dir:
            self._set_status("Selecione a pasta de saída.")
            return
        self._set_busy(True)
        self._set_attr("_progress", 0, self.stateChanged)
        self._set_status("Iniciando processamento...")
        self._log_lines = []
        self.logChanged.emit()
        self._reset_report()

        config = self._build_config()
        overrides = self._build_overrides()

        self._worker_thread = QThread()
        self._worker = PipelineWorker(
            crm_path=self._crm_path or None,
            google_path=self._google_path or None,
            out_dir=self._out_dir,
            config=config,
            overrides=overrides,
            dry_run=dry_run,
        )
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.log.connect(self._append_log)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.cancelled.connect(self._on_cancelled)
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.error.connect(self._worker_thread.quit)
        self._worker.error.connect(self._worker.deleteLater)
        self._worker.cancelled.connect(self._worker_thread.quit)
        self._worker.cancelled.connect(self._worker.deleteLater)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.start()

    @Slot()
    def cancelRun(self) -> None:
        if self._worker:
            self._worker.cancel()

    @Slot()
    def openOutputDir(self) -> None:
        if not self._out_dir:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._out_dir))

    @Slot()
    def openReport(self) -> None:
        if not self._report_path:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._report_path))

    @Slot()
    def copySummary(self) -> None:
        if not self._summary_text:
            return
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self._summary_text)

    def _on_validation_finished(self, result: dict[str, Any]) -> None:
        self._validation_result = result
        self._validation_error = ""
        self._preview_has_mojibake = bool(result.get("preview_has_mojibake"))
        preview_rows = result.get("preview_rows", [])
        formatted_rows = []
        for row in preview_rows:
            formatted_rows.append({
                "name": row.get("name", ""),
                "ddi": row.get("ddi", ""),
                "phone": row.get("phone", ""),
                "tags": row.get("tags", ""),
                "created": row.get("created", ""),
            })
        self._preview_model.set_items(formatted_rows)
        if result.get("crm") is None and result.get("google") is not None:
            self._set_status("Validação concluída (somente Google).")
        else:
            self._set_status("Validação concluída.")
        self.validationChanged.emit()

    def _reset_validation(self) -> None:
        self._validation_result = {}
        self._validation_error = ""
        self._preview_has_mojibake = False
        self._preview_model.clear()
        self.validationChanged.emit()

    def _on_validation_error(self, message: str) -> None:
        self._validation_error = message
        self._preview_has_mojibake = False
        self._set_status("Falha na validação.")
        self.validationChanged.emit()

    def _on_progress(self, percent: int, status: str) -> None:
        self._set_attr("_progress", percent, self.stateChanged)
        self._set_status(status)

    def _on_finished(self, report: dict[str, Any]) -> None:
        self._set_busy(False)
        self._set_status("Processamento finalizado.")
        self._report_counts = report.get("counts", {})
        self._report_warnings = report.get("warnings", [])
        self._report_outputs = report.get("outputs", [])
        out_dir = Path(self._out_dir)
        self._report_path = str(out_dir / "report.json")
        self._suspects_model.set_items(
            [
                {
                    "reason": item.get("reason", ""),
                    "source": item.get("source", ""),
                    "raw_phone": item.get("raw_phone", ""),
                    "normalized_phone": item.get("normalized_phone", ""),
                    "name": item.get("name", ""),
                    "suggested_fix": item.get("suggested_fix", "") or "",
                    "line": str(item.get("line", "")),
                }
                for item in report.get("suspects", [])
            ]
        )
        self._summary_text = self._build_summary_text(report)
        self.reportChanged.emit()

    def _on_error(self, message: str) -> None:
        self._append_log(f"Erro: {message}")
        self._set_status("Erro no processamento.")
        self._set_busy(False)

    def _on_cancelled(self) -> None:
        self._append_log("Execução cancelada pelo usuário.")
        self._set_status("Cancelado.")
        self._set_busy(False)

    def _build_summary_text(self, report: dict[str, Any]) -> str:
        counts = report.get("counts", {})
        lines = [
            "Resumo da execução:",
            f"Lidos: {counts.get('total_rows', 0)}",
            f"Sem telefone: {counts.get('without_phone', 0)}",
            f"Contatos explodidos: {counts.get('contacts_exploded_total', 0)}",
            f"Duplicados fundidos: {counts.get('duplicates_merged', 0)}",
            f"Suspeitos: {counts.get('suspects', 0)}",
            f"Arquivos gerados: {counts.get('output_files', 0)}",
        ]
        warnings = report.get("warnings", [])
        if warnings:
            lines.append("Avisos:")
            lines.extend(warnings)
        return "\n".join(lines)
