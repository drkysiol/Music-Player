import sys
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QSlider, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist, QMediaContent
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Music Player")
        self.setGeometry(100, 100, 700, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: #b9fbc0; font-size: 13px;")

        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        self.setup_ui()
        self.load_music()

    def setup_ui(self):
        layout = QHBoxLayout()

        self.song_list = QListWidget()
        self.song_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: none;
                border-radius: 15px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #44475a;
            }
        """)
        self.song_list.currentRowChanged.connect(self.song_selected)
        layout.addWidget(self.song_list)

        right_panel = QVBoxLayout()

        self.label_time = QLabel("⏱️ 00:00")
        self.label_title = QLabel("🎵 Tytuł: -")
        self.label_artist = QLabel("🎤 Artysta: -")
        self.label_album = QLabel("💿 Album: -")
        self.label_bitrate = QLabel("🎧 Bitrate: -")
        self.label_mixrate = QLabel("🎚️ Mixrate: -")

        for label in [self.label_time, self.label_title, self.label_artist, self.label_album, self.label_bitrate, self.label_mixrate]:
            right_panel.addWidget(label)

        button_row = QHBoxLayout()
        self.btn_shuffle = self.create_button("🔀", self.toggle_shuffle)
        self.btn_prev = self.create_button("⏮", self.play_previous)
        self.btn_playpause = self.create_button("▶️", self.toggle_play_pause)
        self.btn_next = self.create_button("⏭", self.play_next)
        self.btn_loop = self.create_button("🔁", self.toggle_loop)
        self.btn_delete = self.create_button("❌", self.delete_song)

        for btn in [self.btn_shuffle, self.btn_prev, self.btn_playpause, self.btn_next, self.btn_loop, self.btn_delete]:
            button_row.addWidget(btn)

        right_panel.addLayout(button_row)

        # Volume layout
        volume_layout = QHBoxLayout()
        volume_icon = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #555;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #00ff88;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: #888;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ff88;
                border: none;
                height: 16px;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """)
        volume_layout.addWidget(volume_icon)
        volume_layout.addWidget(self.volume_slider)
        right_panel.addLayout(volume_layout)

        layout.addLayout(right_panel)
        self.setLayout(layout)

    def create_button(self, icon, action):
        button = QPushButton(icon)
        button.clicked.connect(action)
        button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                font-size: 20px;
                border: none;
                border-radius: 30px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        return button

    def load_music(self):
        files = [f for f in os.listdir() if f.endswith(".mp3")]
        for file in files:
            url = QUrl.fromLocalFile(os.path.abspath(file))
            self.playlist.addMedia(QMediaContent(url))
            self.song_list.addItem(file)
        self.player.setPlaylist(self.playlist)
        if files:
            self.playlist.setCurrentIndex(0)

    def toggle_play_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.btn_playpause.setText("▶️")
        else:
            self.player.play()
            self.btn_playpause.setText("⏸")
            self.update_info()
            self.timer.start(1000)

    def play_next(self):
        self.playlist.next()
        self.song_list.setCurrentRow(self.playlist.currentIndex())
        self.toggle_play_pause()

    def play_previous(self):
        self.playlist.previous()
        self.song_list.setCurrentRow(self.playlist.currentIndex())
        self.toggle_play_pause()

    def toggle_loop(self):
        if self.playlist.playbackMode() != QMediaPlaylist.Loop:
            self.playlist.setPlaybackMode(QMediaPlaylist.Loop)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
        self.update_button_styles()

    def toggle_shuffle(self):
        if self.playlist.playbackMode() != QMediaPlaylist.Random:
            self.playlist.setPlaybackMode(QMediaPlaylist.Random)
        else:
            self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
        self.update_button_styles()

    def update_button_styles(self):
        def get_button_style(active):
            border = "2px solid #00ff88" if active else "none"
            return f"""
                QPushButton {{
                    background-color: #3a3a3a;
                    color: white;
                    font-size: 20px;
                    border: {border};
                    border-radius: 30px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: #5a5a5a;
                }}
            """

        self.btn_shuffle.setStyleSheet(get_button_style(self.playlist.playbackMode() == QMediaPlaylist.Random))
        self.btn_loop.setStyleSheet(get_button_style(self.playlist.playbackMode() == QMediaPlaylist.Loop))

    def update_time(self):
        ms = self.player.position()
        seconds = int(ms / 1000)
        mins = seconds // 60
        secs = seconds % 60
        self.label_time.setText(f"⏱️ {mins:02}:{secs:02}")

    def song_selected(self, index):
        if index != -1:
            self.playlist.setCurrentIndex(index)
            self.toggle_play_pause()

    def update_info(self):
        index = self.playlist.currentIndex()
        if index == -1:
            return

        filename = self.song_list.item(index).text()
        file_path = os.path.abspath(filename)
        try:
            audio = MP3(file_path, ID3=EasyID3)
            title = audio.get("title", ["Nieznany utwór"])[0]
            artist = audio.get("artist", ["Nieznany artysta"])[0]
            album = audio.get("album", ["Nieznany album"])[0]
            bitrate = int(audio.info.bitrate / 1000)
            mixrate = int(audio.info.sample_rate)

            duration = int(audio.info.length)
            duration_str = f"{duration // 60:02}:{duration % 60:02}"

            self.label_title.setText(f"🎵 {title}")
            self.label_artist.setText(f"🎤 {artist}")
            self.label_album.setText(f"💿 {album}")
            self.label_time.setText(f"⏱️ 00:00 / {duration_str}")
            self.label_bitrate.setText(f"🎧 {bitrate} kbps")
            self.label_mixrate.setText(f"🎚️ {mixrate} Hz")
        except Exception:
            pass

    def delete_song(self):
        index = self.song_list.currentRow()
        if index >= 0:
            self.playlist.removeMedia(index)
            self.song_list.takeItem(index)
            self.player.stop()
            if self.song_list.count() > 0:
                self.song_list.setCurrentRow(0)
            QMessageBox.information(self, "Usunięto", "Piosenka usunięta z listy.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
