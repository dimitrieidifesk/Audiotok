import os
import threading

import interface
import pygame
from pygame import mixer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QWidget

mutex = threading.Lock()


class PygameMusicThread(QThread):
    def __init__(self, dir, sounds_list: list):
        super().__init__()
        self.sounds_list = sounds_list
        self.dir = dir

    def run(self):
        print("Added in queue:")
        pygame.mixer.init()
        first_track = self.sounds_list[0]
        filename = os.path.join(self.dir, first_track)
        pygame.mixer.music.load(filename)
        print(first_track)
        for file in self.sounds_list[1:]:
            print(file)
            filename = os.path.join(self.dir, file)
            pygame.mixer.music.queue(filename)
        pygame.mixer.music.play()


class Player(QWidget, interface.Ui_Form):
    def __init__(self):
        super(Player, self).__init__()
        self.setupUi(self)

        self.setFixedSize(self.size())

        self.play_btn.clicked.connect(self.play_sound_thread)
        self.pause_btn.clicked.connect(self.pause_sound)
        self.prev_btn.clicked.connect(self.prev_sound)
        self.next_btn.clicked.connect(self.next_sound)
        self.add_btn.clicked.connect(self.add_sound)
        self.stop_btn.clicked.connect(self.stop_sound)
        self.remove_btn.clicked.connect(self.remove_sound)

        self.sound_slider.setMinimum(0)
        self.sound_slider.setMaximum(100)
        self.sound_slider.setValue(30)
        self.sound_slider.valueChanged.connect(self.change_volume)

        self.sound_time_slider.setMinimum(0)
        self.sound_time_slider.setMaximum(100)
        self.sound_time_slider.setValue(0)
        self.sound_time_slider.valueChanged.connect(self.move_sound_time)

        self.listWidget.doubleClicked.connect(self.play_sound_thread)

        self.dir = ""
        self.sound_mixer = mixer
        self.sound_mixer.init()
        self.pause = False
        self.filename = ""
        self.music_playing = False

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.move_time_slider_thread)
        # self.timer.start(100)
        # self.move_time_slider_thread()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        self.add_sound_on_init()

    def play_sound_thread(self):
        self.sound_mixer.music.stop()
        item = self.listWidget.currentItem()
        # if item:
        #    self.filename = os.path.join(self.dir, item.text())
        # else:
        #    self.listWidget.currentRow(0)
        sounds_list = [self.listWidget.item(x).text() for x in range(self.listWidget.count())]
        filename = self.listWidget.item(0).text()
        self.filename = os.path.join(self.dir, filename)

        if item:
            filename = item.text()
        cnt = 0
        for i in sounds_list:
            if filename == i:
                sounds_list = sounds_list[cnt:]
                break
            cnt += 1
        self.music_thread = PygameMusicThread(self.dir, sounds_list)
        self.music_thread.start()
        self.music_playing = True
        self.pause = True
        # music_thread = threading.Thread(target=self.play_sound)
        # music_thread.start()

    def play_sound(self):
        try:
            item = self.listWidget.currentItem()
            mutex.acquire()
            if item:
                self.filename = os.path.join(self.dir, item.text())
            else:
                self.listWidget.currentRow(0)
            mutex.release()
            self.sound_mixer.music.load(self.filename)
            self.sound_mixer.music.play()
            self.music_playing = True
            self.pause = True
        except TypeError:
            pass

    def stop_sound(self):
        self.sound_mixer.music.stop()
        self.pause = False
        self.music_playing = False

    def pause_sound(self):
        if self.pause:
            self.sound_mixer.music.pause()
            self.pause = False
            self.music_playing = False
            return "pause"
        self.sound_mixer.music.unpause()
        self.pause = True
        self.music_playing = True

    def prev_sound(self):
        # Get index of sound in list
        row = self.listWidget.currentRow()
        # Put new row
        self.listWidget.setCurrentRow(row - 1)
        self.play_sound()

    def next_sound(self):
        # Get index of sound in list
        row = self.listWidget.currentRow()
        # Put new row
        self.listWidget.setCurrentRow(row + 1)
        self.play_sound()

    def add_sound(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir:
            self.listWidget.clear()
            for filename in os.listdir(dir):
                if filename.endswith((".wav", ".mp3")):
                    # Add filename in listWidget
                    self.listWidget.addItem(os.path.join(filename))
            self.dir = dir

    def add_sound_on_init(self):
        if "audio" in os.listdir("./"):
            dir = os.getcwd() + "/audio"
            for filename in os.listdir(dir):
                if filename.endswith((".wav", ".mp3")):
                    # Add filename in listWidget
                    self.listWidget.addItem(os.path.join(filename))
            self.dir = dir

    def remove_sound(self):
        row = self.listWidget.currentRow()
        item = self.listWidget.takeItem(row)
        os.remove(self.dir + "/" + item.text())
        del item

    def change_volume(self):
        self.sound_mixer.music.set_volume(self.sound_slider.value() / 100)

    def move_sound_time(self):
        length = self.sound_mixer.Sound(self.filename).get_length()
        # cur_pos = self.sound_mixer.music.get_pos()
        self.sound_mixer.music.stop()
        self.sound_mixer.music.play(start=(length / 100) * self.sound_time_slider.value())


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    player = Player()
    import sys

    player.show()
    sys.exit(app.exec_())
