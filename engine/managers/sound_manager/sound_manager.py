import pygame

SOUND_PATH = "assets/sounds/"
SOUND_EXTENSION = ".wav"
MUSIC_EXTENSION = ".mp3"

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music = None

    def play_music(self, file_name: str):
        if len(file_name) == 0:
            raise ValueError("File cannot be empty")
        if self.music is not None:
            self.music.stop()
        self.music = pygame.mixer.Sound(SOUND_PATH + file_name + MUSIC_EXTENSION)
        self.music.set_volume(0.3)
        self.music.play(-1)

    def add_sound(self, name: str, file_name: str):
        if len(name) == 0:
            raise ValueError("Name cannot be empty")
        if len(file_name) == 0:
            raise ValueError("File cannot be empty")
        if name in self.sounds:
            raise ValueError("Name already exists")
        self.sounds[name] = pygame.mixer.Sound( SOUND_PATH + file_name + SOUND_EXTENSION)

    def play_sound(self, name):
        if name not in self.sounds:
            raise ValueError("Sound does not exist")
        self.sounds[name].play()

    def stop_sound(self, name):
        if name not in self.sounds:
            raise ValueError("Sound does not exist")
        self.sounds[name].stop()
