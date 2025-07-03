import sys
from .keystone import KeystoneSupplier
from .cwr import CwrSupplier
from .seawide import SeawideSupplier


def main():
    try:
        from PyQt6.QtWidgets import (
            QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
            QLabel, QComboBox, QInputDialog, QMessageBox, QLineEdit
        )
    except Exception as exc:  # pragma: no cover - optional GUI deps
        print("PyQt6 is required to run the GUI:", exc)
        return

    suppliers = {
        "Keystone": KeystoneSupplier(),
        "CWR": CwrSupplier(),
        "Seawide": SeawideSupplier(),
    }

    class MainWindow(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Automation Tool")
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Select supplier:"))
            self.combo = QComboBox()
            self.combo.addItems(list(suppliers.keys()))
            layout.addWidget(self.combo)

            btn_layout = QHBoxLayout()
            self.btn_set_cred = QPushButton("Set Credentials")
            self.btn_set_ftp = QPushButton("Set FTP Credentials")
            self.btn_update = QPushButton("Fetch Inventory Update")
            self.btn_full = QPushButton("Fetch Full Inventory")
            self.btn_test = QPushButton("Test Connection")
            btn_layout.addWidget(self.btn_set_cred)
            btn_layout.addWidget(self.btn_set_ftp)
            layout.addLayout(btn_layout)
            layout.addWidget(self.btn_update)
            layout.addWidget(self.btn_full)
            layout.addWidget(self.btn_test)
            self.setLayout(layout)

            self.btn_set_cred.clicked.connect(self.handle_set_cred)
            self.btn_set_ftp.clicked.connect(self.handle_set_ftp)
            self.btn_update.clicked.connect(self.handle_update)
            self.btn_full.clicked.connect(self.handle_full)
            self.btn_test.clicked.connect(self.handle_test)

        def supplier(self):
            name = self.combo.currentText()
            return suppliers[name]

        def handle_set_cred(self):
            sup = self.supplier()
            if isinstance(sup, CwrSupplier):
                feed, ok = QInputDialog.getText(self, "Feed ID", "Feed ID:")
                if ok and feed:
                    sup.set_credential("feed_id", feed)
            else:
                acct, ok = QInputDialog.getText(self, "Account Number", "Account Number:")
                if not ok:
                    return
                key, ok = QInputDialog.getText(self, "Security Key", "Security Key:")
                if ok:
                    sup.set_credential("account_number", acct)
                    sup.set_credential("security_key", key)
            QMessageBox.information(self, "Saved", "Credentials saved")

        def handle_set_ftp(self):
            sup = self.supplier()
            user, ok = QInputDialog.getText(self, "FTP User", "FTP User:")
            if not ok:
                return
            pwd, ok = QInputDialog.getText(self, "FTP Password", "FTP Password:", QLineEdit.EchoMode.Password)
            if not ok:
                return
            folder, ok = QInputDialog.getText(self, "Remote Folder", "Remote Folder:", text=sup.get_credential("ftp_remote_dir", "/"))
            if not ok:
                return
            rfile, ok = QInputDialog.getText(self, "Remote File", "Remote File:", text=sup.get_credential("remote_update_file", "Inventory.csv"))
            if ok:
                sup.set_credential("ftp_user", user)
                sup.set_credential("ftp_password", pwd)
                sup.set_credential("ftp_remote_dir", folder)
                sup.set_credential("remote_update_file", rfile)
                QMessageBox.information(self, "Saved", "FTP credentials saved")

        def handle_update(self):
            sup = self.supplier()
            sup.fetch_inventory()
            QMessageBox.information(self, "Done", "Inventory update complete")

        def handle_full(self):
            sup = self.supplier()
            if hasattr(sup, "fetch_inventory_full"):
                sup.fetch_inventory_full()
                QMessageBox.information(self, "Done", "Full inventory fetched")
            else:
                QMessageBox.warning(self, "N/A", "Full inventory not supported")

        def handle_test(self):
            sup = self.supplier()
            sup.test_connection()

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
