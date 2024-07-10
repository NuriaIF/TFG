"""
This module contains the SoundManager class
"""
import pygame

SOUND_PATH = "assets/sounds/"
SOUND_EXTENSION = ".wav"
MUSIC_EXTENSION = ".mp3"


class SoundManager:
    """
    A class to manage the sound effects and music of the game.
    """
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None

    def play_music(self, file_name: str) -> None:
        """
        Play the music of the game.
        :param file_name:
        :return:
        """
        if len(file_name) == 0:
            raise ValueError("File cannot be empty")
        if self.music is not None:
            self.music.stop()
        self.music = pygame.mixer.Sound(SOUND_PATH + file_name + MUSIC_EXTENSION)
        self.music.set_volume(0.3)
        self.music.play(-1)

    def add_sound(self, name: str, file_name: str) -> None:
        """
        Add a sound to the sound manager.
        :param name: Name of the sound
        :param file_name: File name of the sound
        :return: None
        """
        if len(name) == 0:
            raise ValueError("Name cannot be empty")
        if len(file_name) == 0:
            raise ValueError("File cannot be empty")
        if name in self.sounds:
            raise ValueError("Name already exists")
        self.sounds[name] = pygame.mixer.Sound(SOUND_PATH + file_name + SOUND_EXTENSION)

    def play_sound(self, name: str) -> None:
        """
        Play the sound given by the name, must have been added before by calling add_sound.
        :param name:
        :return:
        """
        if name not in self.sounds:
            raise ValueError("Sound does not exist")
        self.sounds[name].play()

    def stop_sound(self, name) -> None:
        """
        Stop the sound given by the name from playing, must have been added before by calling add_sound.
        :param name:
        :return:
        """
        if name not in self.sounds:
            raise ValueError("Sound does not exist")
        self.sounds[name].stop()
