import sys
import ctypes

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QLabel, QVBoxLayout, QSizePolicy, QProgressBar, QStatusBar, QFileDialog, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

import os
import subprocess
import zipfile
from pathlib import Path

import qtawesome as qta

def resource_path(rel):
    try:
        base = sys._MEIPASS
    except Exception:
        base = Path(__file__).parent
    return str(Path(base) / rel)

APP_INFO = {
    "name": "Pngtree Zipper",
    "version": "1.0.0",
    "developer": "Desainia Studio",
    "license": "MIT",
    "about": "A simple helper tool to zip asset files to submit to Pngtree."
}

STYLES = {
    "drop_area": "border: 2px dashed #4caf50; border-radius: 8px; padding: 24px; min-height: 160px;",
    "drop_area_supported": "border: 2px dashed #2196F3; border-radius: 8px; padding: 24px; min-height: 160px;",
    "drop_area_unsupported": "border: 2px dashed #f44336; border-radius: 8px; padding: 24px; min-height: 160px;",
    "drop_title": "font-size:16px;font-weight:600;",
    "drop_note": "margin-top:12px;font-size:10px;",
    "stats": "font-size:12px;",
    "output": "font-size:12px; color: #888;",
    "progress": "QProgressBar { background-color: rgba(0,0,0,0.2); border-radius: 6px; height: 12px; } QProgressBar::chunk { background-color: #4caf50; border-radius: 6px; }",
    "run_button": "QPushButton { background-color: #4caf50; color: #fff; border-radius: 6px; padding: 6px 12px; font-size:14px; font-weight:600; min-height:28px; } QPushButton:hover { background-color: #43a047; }"
} 

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        drop_html = f"<div style='{STYLES['drop_title']}'>Drag and drop supported files: PSD, AI, EPS, PNG, JPG</div><div style='{STYLES['drop_note']}'>Files with the same name will be zipped into one package.</div>"
        self.drop_area = QLabel(drop_html)
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setWordWrap(True)
        self.drop_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.drop_area.setStyleSheet(STYLES['drop_area'])
        layout.addWidget(self.drop_area)
        self.stats_label = QLabel("Files: 0 | Size: 0B")
        self.stats_label.setAlignment(Qt.AlignLeft)
        self.stats_label.setStyleSheet(STYLES['stats'])
        layout.addWidget(self.stats_label, alignment=Qt.AlignLeft)
        self.output_label = QLabel("Output: (not set)")
        self.output_label.setAlignment(Qt.AlignLeft)
        self.output_label.setStyleSheet(STYLES['output'])
        self.open_output_button = QPushButton(qta.icon('fa6s.folder-open'), "")
        self.open_output_button.setFixedSize(28, 28)
        self.open_output_button.setFlat(True)
        self.open_output_button.setEnabled(False)
        self.open_output_button.clicked.connect(self.open_output)
        col = QVBoxLayout()
        col.addWidget(self.output_label)
        col.addWidget(self.open_output_button, alignment=Qt.AlignLeft)
        layout.addLayout(col)
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        self.overall_progress.setFormat("Overall: %p%")
        self.overall_progress.setStyleSheet(STYLES['progress'])
        layout.addWidget(self.overall_progress)
        self.file_progress = QProgressBar()
        self.file_progress.setRange(0, 100)
        self.file_progress.setValue(0)
        self.file_progress.setTextVisible(True)
        self.file_progress.setFormat("File: %p%")
        self.file_progress.setStyleSheet(STYLES['progress'])
        layout.addWidget(self.file_progress)
        layout.addStretch()
        self.run_button = QPushButton(qta.icon('fa6s.play', color='white'), "Run batch zip")
        self.run_button.setIconSize(QSize(18, 18))
        self.run_button.setStyleSheet(STYLES['run_button'])
        self.run_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.run_button.setMaximumHeight(28)
        layout.addWidget(self.run_button)
        self.setLayout(layout)
        self.setAcceptDrops(True)

    def _check_supported(self, urls):
        files = [url.toLocalFile() for url in urls]
        supported_extensions = ('.psd', '.ai', '.eps', '.png', '.jpg')
        supported_files = [f for f in files if f.lower().endswith(supported_extensions)]
        return files, supported_files

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        files, supported_files = self._check_supported(event.mimeData().urls())
        if supported_files and len(supported_files) == len(files):
            self.drop_area.setStyleSheet(STYLES['drop_area_supported'])
            event.accept()
        elif supported_files:
            self.drop_area.setStyleSheet(STYLES['drop_area_unsupported'])
            event.accept()
        else:
            self.drop_area.setStyleSheet(STYLES['drop_area_unsupported'])
            event.ignore()

    def dragMoveEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        files, supported_files = self._check_supported(event.mimeData().urls())
        if supported_files and len(supported_files) == len(files):
            self.drop_area.setStyleSheet(STYLES['drop_area_supported'])
            event.accept()
        elif supported_files:
            self.drop_area.setStyleSheet(STYLES['drop_area_unsupported'])
            event.accept()
        else:
            self.drop_area.setStyleSheet(STYLES['drop_area_unsupported'])
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet(STYLES['drop_area'])
        event.accept()

    def dropEvent(self, event):
        files, supported_files = self._check_supported(event.mimeData().urls())
        print(f"Dropped supported files: {supported_files}")
        if hasattr(self.window(), 'model'):
            added, skipped = self.window().model.add_files(supported_files)
            all_files = self.window().model.get_all_files()
            self.update_stats(all_files)
            self.window().statusBar().showMessage(f"Added {len(added)} files, skipped {len(skipped)}", 5000)
        else:
            self.update_stats(supported_files)
        self.set_overall_progress(0)
        self.set_file_progress(0)
        self.drop_area.setStyleSheet(STYLES['drop_area'])
        self.window().statusBar().showMessage(f"Dropped {len(supported_files)} supported files", 5000)

    def _human_size(self, n):
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if n < 1024:
                if unit == "B":
                    return f"{n}{unit}"
                return f"{n:.2f}{unit}"
            n /= 1024
        return f"{n:.2f}PB"

    def update_stats(self, files):
        count = len(files)
        total = 0
        for f in files:
            try:
                total += os.path.getsize(f)
            except Exception as e:
                print(f"Error getting size for {f}: {e}")
        self.stats_label.setText(f"Files: {count} | Size: {self._human_size(total)}")

    def set_overall_progress(self, value):
        self.overall_progress.setValue(int(value))

    def set_file_progress(self, value):
        self.file_progress.setValue(int(value))

    def set_output_path(self, path):
        if path:
            self.output_label.setText(f"Output: {path}")
            self.open_output_button.setEnabled(True)
        else:
            self.output_label.setText("Output: (not set)")
            self.open_output_button.setEnabled(False)

    def open_output(self):
        path = None
        if hasattr(self.window(), 'model'):
            path = self.window().model.get_output_dir()
        if not path:
            print("No output directory set")
            self.window().statusBar().showMessage("No output directory set", 5000)
            return
        if sys.platform.startswith('win'):
            os.startfile(path)
            return
        if sys.platform.startswith('darwin'):
            subprocess.Popen(['open', path])
            return
        subprocess.Popen(['xdg-open', path])

class Model:
    def __init__(self):
        self._set = set()
        self.files = []
        self.output_dir = None

    def add_files(self, files):
        added = []
        skipped = []
        for f in files:
            if f in self._set:
                skipped.append(f)
                continue
            self._set.add(f)
            self.files.append(f)
            added.append(f)
        return added, skipped

    def clear_files(self):
        self._set.clear()
        self.files.clear()

    def get_all_files(self):
        return list(self.files)

    def set_output_dir(self, path):
        self.output_dir = path

    def get_output_dir(self):
        return self.output_dir

class View(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pngtree Zipper")
        self.setWindowIcon(QIcon(resource_path("pngtree_zipper.ico")))
        self.resize(400, 300)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        self.import_action = file_menu.addAction(qta.icon('fa6s.file-import'), "Import files")
        file_menu.addAction(qta.icon('fa6s.folder-open'), "Select Folder")
        self.output_dir_action = file_menu.addAction(qta.icon('fa6s.folder'), "Output Directory")
        self.clear_action = file_menu.addAction(qta.icon('fa6s.trash'), "Clear data")
        exit_action = file_menu.addAction(qta.icon('fa6s.right-from-bracket'), "Exit")
        exit_action.triggered.connect(self.close)
        about_action = self.menu_bar.addAction("About")
        about_action.triggered.connect(self.show_about)
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        window_size = self.frameGeometry()
        center_point = screen.center()
        window_size.moveCenter(center_point)
        self.move(window_size.topLeft())

    def show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        icon = QIcon(resource_path("pngtree_zipper.ico"))
        pix = icon.pixmap(64, 64)
        msg.setIconPixmap(pix)
        msg.setWindowIcon(icon)
        msg.setText(f"{APP_INFO['name']} v{APP_INFO['version']}\n\nDeveloper: {APP_INFO['developer']}\nLicense: {APP_INFO['license']}\n\n{APP_INFO['about']}")
        msg.exec()

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.model = self.model
        self.view.import_action.triggered.connect(self.import_files)
        self.view.output_dir_action.triggered.connect(self.choose_output_directory)
        self.view.clear_action.triggered.connect(self.clear_data)
        self.view.main_widget.run_button.clicked.connect(self.run_batch_zip)

    def clear_data(self):
        self.model.clear_files()
        self.model.set_output_dir(None)
        self.view.main_widget.set_output_path(None)
        self.view.main_widget.update_stats(self.model.get_all_files())
        self.view.main_widget.set_overall_progress(0)
        self.view.main_widget.set_file_progress(0)
        self.view.statusBar().showMessage("Cleared data and output directory", 5000)

    def import_files(self):
        files, _ = QFileDialog.getOpenFileNames(self.view, "Import files", str(Path.home()), "Supported files (*.psd *.ai *.eps *.png *.jpg);;All files (*)")
        if not files:
            return
        added, skipped = self.model.add_files(files)
        self.view.main_widget.update_stats(self.model.get_all_files())
        self.view.main_widget.set_overall_progress(0)
        self.view.main_widget.set_file_progress(0)
        self.view.statusBar().showMessage(f"Imported {len(added)} files, skipped {len(skipped)}", 5000)

    def choose_output_directory(self):
        path = QFileDialog.getExistingDirectory(self.view, "Select output directory", str(Path.home()))
        if not path:
            return False
        self.model.set_output_dir(path)
        self.view.main_widget.set_output_path(path)
        self.view.statusBar().showMessage(f"Output directory set: {path}", 5000)
        return True

    def run_batch_zip(self):
        files = self.model.get_all_files()
        if not files:
            print("No files to process")
            self.view.statusBar().showMessage("No files to process", 5000)
            return
        output_dir = self.model.get_output_dir()
        parents = {Path(f).parent for f in files}
        if not output_dir:
            if len(parents) == 1:
                    output_dir = parents.pop()
                    self.model.set_output_dir(str(output_dir))
                    self.view.main_widget.set_output_path(str(output_dir))
                    self.view.statusBar().showMessage(f"Using source folder as output: {output_dir}", 5000)
                    print(f"Using source folder as output: {output_dir}")
            else:
                    path = QFileDialog.getExistingDirectory(self.view, "Select output directory", str(Path.home()))
                    if not path:
                        print("No output directory selected")
                        self.view.statusBar().showMessage("No output directory selected", 5000)
                        return
                    output_dir = path
                    self.model.set_output_dir(output_dir)
                    self.view.main_widget.set_output_path(output_dir)
                    self.view.statusBar().showMessage(f"Output directory set: {output_dir}", 5000)
        self.view.main_widget.run_button.setEnabled(False)
        supported_extensions = ('.psd', '.ai', '.eps', '.png', '.jpg')
        groups = {}
        parents_map = {}
        for f in files:
            try:
                resolved = str(Path(f).resolve())
            except Exception:
                resolved = str(Path(f))
            stem = Path(resolved).stem
            groups.setdefault(stem, set()).add(resolved)
            parents_map.setdefault(stem, set()).add(Path(resolved).parent)
        for stem, items in list(groups.items()):
            found = set(items)
            for parent in parents_map.get(stem, set()):
                try:
                    for p in parent.iterdir():
                        try:
                            if p.is_file() and p.stem == stem and p.suffix.lower() in supported_extensions:
                                found.add(str(p.resolve()))
                        except Exception:
                            try:
                                if p.is_file() and p.stem == stem and p.suffix.lower() in supported_extensions:
                                    found.add(str(p))
                            except Exception as e:
                                print(f"Error checking file {p}: {e}")
                except Exception as e:
                    print(f"Error scanning directory {parent}: {e}")
            groups[stem] = list(found)
        all_included = []
        for items in groups.values():
            all_included.extend(items)
        self.view.main_widget.update_stats(all_included)
        total_groups = len(groups)
        completed_groups = 0
        for stem, items in groups.items():
            zip_path = Path(output_dir) / f"{stem}.zip"
            try:
                with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                    unique_items = []
                    seen_names = set()
                    for src in items:
                        name = Path(src).name
                        if name in seen_names:
                            continue
                        seen_names.add(name)
                        unique_items.append(src)
                    for idx, src in enumerate(unique_items, start=1):
                        try:
                            current_file_name = Path(src).name
                            file_pct = int((idx / len(unique_items)) * 100)
                            overall_pct = int(((completed_groups) + (idx / len(unique_items))) / total_groups * 100) if total_groups else 100
                            self.view.main_widget.file_progress.setFormat(f"Zipping: {current_file_name} (%p%)")
                            self.view.main_widget.set_file_progress(file_pct)
                            self.view.main_widget.overall_progress.setFormat(f"Overall: {completed_groups+1}/{total_groups} (%p%)")
                            self.view.main_widget.set_overall_progress(overall_pct)
                            zf.write(src, arcname=current_file_name)
                        except Exception as e:
                            print(f"Error adding {src} to {zip_path}: {e}")
                completed_groups += 1
                self.view.main_widget.set_overall_progress(int((completed_groups / total_groups) * 100))
                self.view.main_widget.overall_progress.setFormat(f"Completed: {completed_groups}/{total_groups} (%p%)")
            except Exception as e:
                print(f"Error creating {zip_path}: {e}")
        self.view.main_widget.set_overall_progress(100)
        self.view.main_widget.set_file_progress(100)
        self.view.statusBar().showMessage(f"Completed {completed_groups} zip(s)", 5000)
        print(f"Completed {completed_groups} zip(s)")
        self.view.main_widget.run_button.setEnabled(True)

if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PngtreeZipper")
    app = QApplication(sys.argv)
    model = Model()
    view = View()
    controller = Controller(model, view)
    view.center_window()
    view.show()
    sys.exit(app.exec())