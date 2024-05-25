from pygame import Vector2

from game.ai.ai_agent import AIAgent
from game.ai.ai_input_manager import AIInputManager
from game.ai.neural_network.neural_network import NeuralNetwork
from game.entities.car import Car
from game.game_state.game_state import GameState
from game.ai.genetic_algorithm.genetic_algorithm import GeneticAlgorithm


class AIManager:
    def __init__(self, initialization_callback, training=True):
        self.generation_duration: int = 100
        self.initial_state_for_this_generation: GameState = GameState()
        # self.neural_networks: list[NeuralNetwork] = []
        # self.ai_agents: list[AIAgent] = []
        self.current_agent_index = 0
        self.population_size = 10
        self.training = training
        if training:
            self.genetic_algorithm: GeneticAlgorithm = GeneticAlgorithm()
            self.initialization_entities_callback = initialization_callback
        self._agents: list[AIAgent] = []
        self.state = "simulation"

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

    def get_agents(self):
        return self.genetic_algorithm.get_agents()

    def update(self, cars: list[Car]):
        # self.prepare_input(game_state)
        # if not self.genetic_algorithm.get_agents():
        if not self.get_agents():
            self.create_population(cars)
        if self.state == "simulation":
            self.simulate()
        elif self.state == "selection":
            self.select_agents()
        elif self.state == "evolving":
            self.evolve_agents()
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
        if self.state == "simulation":
            for agent in self.get_agents():
                agent.evaluate_fitness()
                inputs = self.prepare_input(agent.controlled_entity)
                outputs = agent.neural_network.forward(inputs)
                # TODO: Convert outputs to commands
                agent.ai_input_manager.convert_outputs_to_commands(outputs)

            if not self.training:
                return

        # Evolve best agent
        # TODO: check if generation is over
        # check if generation is over
        self.genetic_algorithm.generation_timer += 1
        if self.genetic_algorithm.generation_timer >= self.genetic_algorithm.generation_duration:
            self.state = "selection"
            for agent in self.get_agents():
                agent.ai_input_manager.stop_keys()

    def select_agents(self):
        self.genetic_algorithm.select_agents()
        if self.genetic_algorithm.end_of_selection:
            self.state = "evolving"
            self.genetic_algorithm.end_of_selection = False

    def evolve_agents(self):
        self.genetic_algorithm.evolve_agents()
        self.state = "simulation"
        # self._agents = self.genetic_algorithm.get_agents()
        self.genetic_algorithm.generation_timer = 0
        self.initialization_entities_callback()

    def prepare_input(self, car: Car):
        """
        Prepare the input for the neural network
        :param car: Car
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
        if len(cars) == 1:
            self.get_agents().append(AIAgent(cars[0], NeuralNetwork(layer_sizes=[292, 150, 60, 6])))
            self.get_agents()[0].neural_network.load_parameters()
            return
        for i in range(self.population_size):
            self.get_agents().append(
                AIAgent(cars[i], NeuralNetwork(layer_sizes=[292, 150, 60, 6])))  # FOV 12x12, radius=6
            self.genetic_algorithm.load_agents(self.get_agents())

    def get_ai_input_manager_of(self, car: Car) -> AIInputManager:
        for agent in self.get_agents():
            if agent.controlled_entity == car:
                return agent.ai_input_manager
