from pygame import Vector2

from game.ai.ai_agent import AIAgent
from game.ai.neural_network.neural_network import NeuralNetwork
from game.entities.car import Car
from game.game_state.game_state import GameState
from game.ai.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class AIManager:
    def __init__(self, initialization_callback):
        self.generation_duration: int = 100
        self.initial_state_for_this_generation: GameState = GameState()
        # self.neural_networks: list[NeuralNetwork] = []
        # self.ai_agents: list[AIAgent] = []
        self.current_agent_index = 0
        self.population_size = 10
        self.genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm(initialization_callback)

        # self.num_generations = 10
        # self.current_generation = 0
        # self.genome_length = 5
        # self.mutation_rate = 0.1
        # self.nn_input = 5
        # self.nn_hidden = 5
        # self.nn_output = 1
        # self.create_population()

    def get_population_size(self):
        return self.population_size

    def update(self, cars: list[Car]):
        # self.prepare_input(game_state)
        if not self.genetic_algorithm.get_agents():
            self.create_population(cars)
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
        for agent in self.genetic_algorithm.get_agents():
            inputs = self.prepare_input(agent.controlled_entity)
            outputs = agent.neural_network.forward(inputs)
            # TODO: Convert outputs to commands
        # Evolve best agent
        # TODO: check if generation is over
        if True:
            self.genetic_algorithm.evolve_agents()
        # 0. Si es el primer agente, guardar game_state
        # if self.current_agent_index == 0:
        #     self.save_game
        # 1. Coger el game state y el fov y sacar los inputs
        # 2. Pasar los inputs por la red neuronal y sacar outputs
        # 3. Convertir outputs a comandos a través del ai_input_manager
        # 4. Si el agente no se puede mover, pasar al siguiente agente, y avisar a game de cambiar su game_state por el que tenemos aqui guardado
        # condition = True
        # if condition:
            # self.next_agent()
        # 5. Al terminar todos los agentes, ver cual tuvo mejor desempeño
        # if self.current_agent_index == -1:
        #     self.evaluate()
        # 6. Start new gen


    def prepare_input(self, car: Car):
        """
        Prepare the input for the neural network
        :param game_state:
        :return:
        """
        entity = car.car_entity
        agent_forward: Vector2 = entity.get_transform().get_forward()
        agent_velocity: float = entity.get_physics().get_velocity()
        agent_acceleration: float = entity.get_physics().get_acceleration()
        agent_field_of_view: list[float] = car.field_of_view.get_encoded_version()

        inputs = [agent_forward.x, agent_forward.y, agent_velocity, agent_acceleration]
        inputs.extend(agent_field_of_view)

        return inputs

        # print(len(inputs))
        # print(len(agent_field_of_view))

        # game_state = GameState()
        # game_state.update(agent, game, tilemap)
        # 
        # inputs = [game_state.agent_forward, game_state.agent_velocity, game_state.agent_acceleration]
        # inputs.extend(game_state.mapinfo)
        # return inputs

    def create_population(self, cars: list[Car]):
        """
        Initialize population
        :return:
        """
        for i in range(self.population_size):
            self.genetic_algorithm.get_agents().append(AIAgent(cars[i], NeuralNetwork(layer_sizes=[292, 150, 60, 6])))  # FOV 12x12, radius=6

    # def calculate_field_of_vision(self, tiles_within_square, npcs_within_square) -> list[float]:
    #     # tiles = tile_map.get_tiles_within_square((self.agent_position.x, self.agent_position.y), vision_range)
    #     # npcs = game.get_npcs_within_square(tiles)
    #     tiles = tiles_within_square
    #     npcs = npcs_within_square
    # 
    #     map_info = []
    # 
    #     for tile, npc in zip(tiles, npcs):
    #         if tile is None:
    #             map_info.append(-1)
    #         elif tile.tile_type == MapType.GRASS:
    #             map_info.append(-0.75)
    #         elif tile.tile_type == MapType.SIDEWALK:
    #             map_info.append(-0.5)
    #         elif tile.tile_type == MapType.TRACK:
    #             map_info.append(1)
    # 
    #         if npc is None:
    #             map_info.append(0)
    #         else:
    #             map_info.append(1)
    #     
    #     print(map_info)
    #     print(len(map_info))
    # 
    #     return map_info
