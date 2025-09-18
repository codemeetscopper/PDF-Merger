import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from pypdf import PdfReader, PdfWriter


class PdfMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.setMinimumSize(700, 400)

        layout = QVBoxLayout(self)

        # Toolbar buttons
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add PDFs")
        self.btn_add.clicked.connect(self.load_pdfs)
        self.btn_clear = QPushButton("🗑 Clear List")
        self.btn_clear.clicked.connect(self.clear_list)
        self.btn_merge = QPushButton("📑 Merge")
        self.btn_merge.clicked.connect(self.merge_pdfs)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_clear)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_merge)
        layout.addLayout(toolbar)

        # Table for PDFs
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["PDF File", "Pages (e.g. 1-3,5)", ""])
        self.table.horizontalHeader().setStretchLastSection(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 80)

        layout.addWidget(self.table)

    def load_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDF Files", "", "PDF Files (*.pdf)"
        )
        for file in files:
            reader = PdfReader(file)
            row = self.table.rowCount()
            self.table.insertRow(row)

            # File name cell
            item = QTableWidgetItem(file)
            item.setFlags(Qt.ItemIsEnabled)  # read-only
            self.table.setItem(row, 0, item)

            # Page selection input
            page_input = QLineEdit()
            page_input.setPlaceholderText(f"1-{len(reader.pages)} or leave empty = all")
            self.table.setCellWidget(row, 1, page_input)

            # Remove button
            btn_remove = QPushButton("Remove")
            btn_remove.clicked.connect(lambda _, r=row: self.remove_row(r))
            self.table.setCellWidget(row, 2, btn_remove)

    def remove_row(self, row):
        self.table.removeRow(row)

    def clear_list(self):
        self.table.setRowCount(0)

    def parse_pages(self, text, max_pages):
        """Convert page range string into list of integers."""
        pages = set()
        if not text.strip():
            return list(range(1, max_pages + 1))
        for part in text.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                pages.update(range(int(start), int(end) + 1))
            else:
                pages.add(int(part))
        return [p for p in sorted(pages) if 1 <= p <= max_pages]

    def merge_pdfs(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No PDF files added.")
            return

        writer = PdfWriter()
        for row in range(self.table.rowCount()):
            file = self.table.item(row, 0).text()
            page_input = self.table.cellWidget(row, 1).text()
            reader = PdfReader(file)
            try:
                selected_pages = self.parse_pages(page_input, len(reader.pages))
                for p in selected_pages:
                    writer.add_page(reader.pages[p - 1])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Invalid page selection in {file}: {e}")
                return

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)"
        )
        if save_path:
            with open(save_path, "wb") as f:
                writer.write(f)
            QMessageBox.information(self, "Success", f"Merged PDF saved at:\n{save_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfMergerApp()
    window.show()
    sys.exit(app.exec())
