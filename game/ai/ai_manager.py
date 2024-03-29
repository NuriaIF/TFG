from game.ai.neural_network.neural_network import NeuralNetwork
from game.game_state.game_state import GameState
from game.ai.genetic_algorithm import GeneticAlgorithm
from game.map.map_types import MapType


class AIManager:
    def __init__(self, restore_previous_state_callback):
        self.generation_duration: int = 100
        self.initial_state_for_this_generation: GameState = GameState()
        self.neural_networks: list[NeuralNetwork] = []
        self.current_agent_index = 0
        self.population_size = 10
        self.genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm(self.population_size)

        self.restore_previous_state_callback = restore_previous_state_callback
        # self.num_generations = 10
        # self.current_generation = 0
        # self.genome_length = 5
        # self.mutation_rate = 0.1
        # self.nn_input = 5
        # self.nn_hidden = 5
        # self.nn_output = 1
        # self.create_population()

    def update(self, game_state: GameState):
        # self.prepare_input(game_state)
        if not self.neural_networks:
            self.create_population()
        self.simulate()

    # def next_agent(self):
    #     if self.current_agent_index < len(self.neural_networks) - 1:
    #         self.current_agent_index += 1
    #     else:
    #         self.current_agent_index = -1
    # 
    # def save_game_state(self, game_state):
    #     self.initial_state_for_this_generation = game_state

    def simulate(self):
        # for agent in self.ai_agents:
        #     self.prepare_input(agent, game, tilemap)
        # 0. Si es el primer agente, guardar game_state
        if self.current_agent_index == 0:
            self.save_game
        # 1. Coger el game state y el fov y sacar los inputs
        # 2. Pasar los inputs por la red neuronal y sacar outputs
        # 3. Convertir outputs a comandos a través del ai_input_manager
        # 4. Si el agente no se puede mover, pasar al siguiente agente, y avisar a game de cambiar su game_state por el que tenemos aqui guardado
        condition = True
        if condition:
            self.next_agent()
            self.restore_previous_state_callback(self.initial_state_for_this_generation)
        # 5. Al terminar todos los agentes, ver cual tuvo mejor desempeño
        if self.current_agent_index == -1:
            self.evaluate()
        # 6. Start new gen
            

    def prepare_input(self, game_state):
        """
        Prepare the input for the neural network
        :param game_state:
        :return:
        """
        game_state = GameState()
        game_state.update(agent, game, tilemap)

        inputs = [game_state.agent_forward, game_state.agent_velocity, game_state.agent_acceleration]
        inputs.extend(game_state.mapinfo)
        return inputs

    def create_population(self):
        """
        Initialize population
        :return:
        """
        for i in range(self.population_size):
            new_nn = NeuralNetwork([]) # FOV 12x12
        pass

    def calculate_field_of_vision(self, tiles_within_square, npcs_within_square) -> list[float]:
        # tiles = tile_map.get_tiles_within_square((self.agent_position.x, self.agent_position.y), vision_range)
        # npcs = game.get_npcs_within_square(tiles)
        tiles = tiles_within_square
        npcs = npcs_within_square

        map_info = []

        for tile, npc in zip(tiles, npcs):
            if tile is None:
                map_info.append(-1)
            elif tile.tile_type == MapType.GRASS:
                map_info.append(-0.75)
            elif tile.tile_type == MapType.SIDEWALK:
                map_info.append(-0.5)
            elif tile.tile_type == MapType.TRACK:
                map_info.append(1)

            if npc is None:
                map_info.append(0)
            else:
                map_info.append(1)
        
        print(map_info)
        print(len(map_info))

        return map_info
