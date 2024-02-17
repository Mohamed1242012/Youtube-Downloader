import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QCheckBox
)
from pytube import YouTube
from pytube.exceptions import RegexMatchError

class YouTubeDownloaderApp(QMainWindow):

    def __init__(self):

        def find_file(file_name):
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Iterate through the files in the current directory
            for root, dirs, files in os.walk(current_dir):
                if file_name in files:
                    return os.path.join(root, file_name)
            
            return None

        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setFixedSize(500, 300)  # Set the window size here

        # Set application icon
        file_path = find_file("logo.png")
        self.setWindowIcon(QIcon(file_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.url_label = QLabel("Enter YouTube URL:")
        layout.addWidget(self.url_label)
        self.url_entry = QLineEdit()
        layout.addWidget(self.url_entry)

        self.resolution_label = QLabel("Select Resolution:")
        layout.addWidget(self.resolution_label)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["144p", "240p", "360p", "480p", "720p", "1080p"])
        layout.addWidget(self.resolution_combo)

        self.audio_label = QLabel("Select Option:")
        layout.addWidget(self.audio_label)
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["Video", "Audio"])
        layout.addWidget(self.audio_combo)

        directory_layout = QHBoxLayout()
        layout.addLayout(directory_layout)
        self.directory_label = QLabel("Download Directory:")
        directory_layout.addWidget(self.directory_label)
        self.directory_entry = QLineEdit()
        directory_layout.addWidget(self.directory_entry)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        directory_layout.addWidget(self.browse_button)

        self.open_check = QCheckBox("Open video after downloading")
        layout.addWidget(self.open_check)

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)


    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_entry.setText(directory)

    

    def download(self):
        url = self.url_entry.text()
        directory = self.directory_entry.text()
        resolution = self.resolution_combo.currentText()
        download_audio = self.audio_combo.currentText() == "Audio"

        if not url or not directory:
            QMessageBox.critical(self, "Error", "Please fill all fields")
            return

        if not os.path.exists(directory):
            QMessageBox.critical(self, "Error", "Selected directory does not exist")
            return

        try:
            yt = YouTube(url)
            title = self.sanitize_filename(yt.title)
            stream = None
            if download_audio:
                stream = yt.streams.filter(only_audio=True).first()
            else:
                stream = yt.streams.filter(res=resolution, progressive=True).first()

            if stream is None:
                QMessageBox.critical(self, "Error", f"The video you selected doesn't have {resolution} resolution.")
                return

            file_extension = stream.mime_type.split("/")[-1]
            file_path = os.path.join(directory, f"{title}.{file_extension}")
            stream.download(output_path=directory, filename=file_path)
            self.status_label.setText("Download completed successfully!")
            if self.open_check.isChecked():
                os.startfile(file_path)  # Open the file using the default application
        except RegexMatchError:
            QMessageBox.critical(self, "Error", "The YouTube link you inserted is not valid.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error downloading video: {e}")

    def sanitize_filename(self, filename):
        # Remove characters that may affect Windows Explorer
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
