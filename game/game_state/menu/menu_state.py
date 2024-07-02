import pygame
from overrides import overrides

from engine.managers.input_manager.key import Mouse
from game.game_state.igame_state import IGameState
from game.game_state.menu.menu_actions.exit_game_command import ExitGameCommand
from game.game_state.menu.menu_actions.start_play_command import StartPlayCommand
from game.game_state.menu.menu_actions.start_player_vs_ai_command import StartPlayerVsAICommand
from game.game_state.menu.menu_actions.start_train_ai_command import StartTrainAICommand
from game.game_state.menu.menu_actions.start_watch_ai_command import StartWatchAICommand
from game.game_state.menu.menu_actions.swap_map_next_command import SwapMapNextCommand
from game.game_state.menu.menu_actions.swap_map_previous_command import SwapMapPreviousCommand


class MenuState(IGameState):
    def __init__(self, _game, state_enum):
        super().__init__(_game, state_enum)
        self.right_triangle_rect = None
        self.left_triangle_rect = None
        self.map_name_position = None
        self.image_rect = None
        self.buttons = None
        self.font = None
        self.color_text = (255, 255, 255)
        self.size_text = 25
        self.pressed = False
        self.maps_path = "assets/tracks/tracks_images/"
        self.maps_names = ["road01", "road02", "road03"]
        self.maps = []
        self.map_name_rect = None
        self.current_map_index = 0
        self.buttons_color_border = (255, 255, 255)
        self.buttons_color = (0, 0, 0)

    @overrides
    def initialize(self):
        self.setup_menu()

    @overrides
    def update(self, delta_time):
        mouse_pressed = self._game.get_input_manager().is_mouse_button_pressed(Mouse.MOUSE_LEFT)
        if mouse_pressed and not self.pressed:
            self.handle_mouse_event(self._game.get_input_manager().get_mouse_position())
            self.pressed = True
        elif not mouse_pressed:
            self.pressed = False

    @overrides
    def render(self):
        for button in self.buttons:
            self._game.renderer.draw_rect_absolute(button['rect'], self.buttons_color, 0)
            self._game.renderer.draw_rect_absolute(button['rect'], self.buttons_color_border, 5)
            self._game.renderer.draw_text_absolute(button['text'], button['rect'].center, color=self.color_text,
                                                   size=self.size_text, centered=True)

        # Renderizar la imagen y el nombre del mapa
        self._game.renderer.draw_image_absolute(self.maps[self.current_map_index], self.image_rect.topleft)
        self._game.renderer.draw_rect_absolute(self.image_rect, (0, 0, 0), 5)

        self._game.renderer.draw_text_absolute(self.maps_names[self.current_map_index], self.map_name_position,
                                               color=self.color_text,
                                               size=self.size_text, centered=True)

    @overrides
    def render_debug(self):
        pass

    @overrides
    def destruct(self):
        self.buttons = []
        self.maps = []
        print("Exiting Menu State")

    def handle_mouse_event(self, mouse_pos):
        for button in self.buttons:
            if button['rect'].collidepoint(mouse_pos):
                button['command'].execute()

    def setup_menu(self):
        print("Setting up Menu State")
        self.font = pygame.font.SysFont("Arial", 48)

        self.image_rect = pygame.Rect(400, 50, 700, 420)  # 100, 60
        for i in range(len(self.maps_names)):
            self.maps.append(pygame.image.load(self.maps_path + self.maps_names[i] + ".png"))
            self.maps[i] = pygame.transform.scale(self.maps[i], self.image_rect.size)
            self.maps[i] = pygame.transform.flip(self.maps[i], False, True)

        self.map_name_position = (self.image_rect.x + self.image_rect.width / 2,
                                  self.image_rect.y + self.image_rect.height + 50)

        self.map_name_rect = pygame.Rect(self.map_name_position[0] - 50,
                                         self.map_name_position[1] - 25,
                                         100, 50)

        distance_between_buttons = 70
        self.buttons = [
            self.create_button("Play", (50, 50),
                               StartPlayCommand(self, self._game)),
            self.create_button("Player vs. AI", (50, 50 + distance_between_buttons),
                               StartPlayerVsAICommand(self, self._game)),
            self.create_button("Watch AI", (50, 50 + 2 * distance_between_buttons),
                               StartWatchAICommand(self, self._game)),
            self.create_button("Train new AI", (50, 50 + 3 * distance_between_buttons),
                               StartTrainAICommand(self, self._game)),
            self.create_button("<", (self.map_name_position[0] - 150 - 50 / 2,
                                     self.map_name_position[1] - 50 / 2),
                               size=(50, 50), command=SwapMapPreviousCommand(self)),
            self.create_button(">", (self.map_name_position[0] + 150 - 50 / 2,
                                     self.map_name_position[1] - 50 / 2),
                               size=(50, 50), command=SwapMapNextCommand(self)),
            self.create_button("Exit", (50, 50 + 9 * distance_between_buttons), ExitGameCommand(self._game))
        ]

    def create_button(self, text, topleft, command, size=(200, 50)):
        button_rect = pygame.Rect(topleft, size)
        return {
            'rect': button_rect,
            'text': text,
            'command': command
        }
