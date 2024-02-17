# Import necessary modules
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

# Define the main application class
class YouTubeDownloaderApp(QMainWindow):

    # Initialize the application
    def __init__(self):

        # Define a function to find a file in the current directory
        def find_file(file_name):
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Iterate through the files in the current directory
            for root, dirs, files in os.walk(current_dir):
                if file_name in files:
                    return os.path.join(root, file_name)
            
            return None

        # Call the constructor of the parent class
        super().__init__()

        # Set the title and size of the window
        self.setWindowTitle("YouTube Downloader")
        self.setFixedSize(500, 300)  # Set the window size here

        # Set application icon
        file_path = find_file("logo.png")
        self.setWindowIcon(QIcon(file_path))

        # Create a central widget for the window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a label and an entry field for the YouTube URL
        self.url_label = QLabel("Enter YouTube URL:")
        layout.addWidget(self.url_label)
        self.url_entry = QLineEdit()
        layout.addWidget(self.url_entry)

        # Create a label and a combo box for selecting the video resolution
        self.resolution_label = QLabel("Select Resolution:")
        layout.addWidget(self.resolution_label)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["144p", "240p", "360p", "480p", "720p", "1080p"])
        layout.addWidget(self.resolution_combo)

        # Create a label and a combo box for selecting the download option (video or audio)
        self.audio_label = QLabel("Select Option:")
        layout.addWidget(self.audio_label)
        self.audio_combo = QComboBox()
        self.audio_combo.addItems(["Video", "Audio"])
        layout.addWidget(self.audio_combo)

        # Create a layout for the directory selection
        directory_layout = QHBoxLayout()
        layout.addLayout(directory_layout)
        self.directory_label = QLabel("Download Directory:")
        directory_layout.addWidget(self.directory_label)
        self.directory_entry = QLineEdit()
        directory_layout.addWidget(self.directory_entry)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_directory)
        directory_layout.addWidget(self.browse_button)

        # Create a checkbox for the option to open the video after downloading
        self.open_check = QCheckBox("Open video after downloading")
        layout.addWidget(self.open_check)

        # Create a button for starting the download
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download)
        layout.addWidget(self.download_button)

        # Create a label for displaying the download status
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    # Function to handle the directory browsing
    def browse_directory(self):
        # Open a dialog to select a directory
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory_entry.setText(directory)

    # Function to handle the download process
    def download(self):
        # Get the URL, directory, resolution, and download option
        url = self.url_entry.text()
        directory = self.directory_entry.text()
        resolution = self.resolution_combo.currentText()
        download_audio = self.audio_combo.currentText() == "Audio"

        # Check if the URL and directory are provided
        if not url or not directory:
            QMessageBox.critical(self, "Error", "Please fill all fields")
            return

        # Check if the directory exists
        if not os.path.exists(directory):
            QMessageBox.critical(self, "Error", "Selected directory does not exist")
            return

        try:
            # Create a YouTube object from the provided URL
            yt = YouTube(url)
            # Get the title of the video and sanitize it for use as a file name
            title = self.sanitize_filename(yt.title)
            # Get the appropriate stream based on the download option
            stream = None
            if download_audio:
                stream = yt.streams.filter(only_audio=True).first()
            else:
                stream = yt.streams.filter(res=resolution, progressive=True).first()

            # Check if a stream is available
            if stream is None:
                QMessageBox.critical(self, "Error", f"The video you selected doesn't have {resolution} resolution.")
                return

            # Get the file extension and create the file path
            file_extension = stream.mime_type.split("/")[-1]
            file_path = os.path.join(directory, f"{title}.{file_extension}")
            # Download the stream to the specified directory
            stream.download(output_path=directory, filename=file_path)
            # Display a success message
            self.status_label.setText("Download completed successfully!")
            # Open the video if the checkbox is checked
            if self.open_check.isChecked():
                os.startfile(file_path)  # Open the file using the default application
        except RegexMatchError:
            QMessageBox.critical(self, "Error", "The YouTube link you inserted is not valid.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error downloading video: {e}")

    # Function to sanitize a filename by removing invalid characters
    def sanitize_filename(self, filename):
        # Remove characters that may affect Windows Explorer
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        return filename

# Main function to start the application
def main():
    # Create a QApplication object
    app = QApplication(sys.argv)
    # Create an instance of the main window
    window = YouTubeDownloaderApp()
    # Show the main window
    window.show()
    # Start the application event loop
    sys.exit(app.exec_())

# Check if the script is being run as the main program
if __name__ == "__main__":
    # Call the main function
    main()
