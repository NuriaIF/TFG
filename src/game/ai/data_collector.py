"""
This module contains the DataCollector class, which is responsible for collecting and saving data about the fitness of
"""
import csv
import json

from src.game.ai.ai_info.interval import Interval


class DataCollector:
    """
    The DataCollector class is responsible for collecting and saving data about the fitness of the agents.
    """
    def __init__(self):
        self.generation_intervals: list[Interval] = []
        self.generation_intervals.append(Interval(0, 0))
        self.top_fitness_per_generation = []

        self.total_fitness_per_car_through_time = {}

    def collect_fitness(self, agent, elapsed_time, evaluate=True, new_generation=False):
        """
        Collect the fitness of the agent.
        :param agent: agent to collect the fitness from
        :param elapsed_time: elapsed time of the simulation
        :param evaluate: whether to evaluate the fitness of the agent
        :param new_generation: whether the agent is in a new generation
        """
        if new_generation:
            self._update_fitness(agent.controlled_entity.entity_ID, elapsed_time + 0.001, 0)
        if evaluate:
            fitness_score = agent.evaluate_fitness()
        else:
            fitness_score = agent.fitness_score

        self._update_fitness(agent.controlled_entity.entity_ID, elapsed_time, fitness_score)

    def change_generation(self, elapsed_time, agents, current_generation):
        """
        Change the generation of the agents and save the data.
        :param elapsed_time: elapsed time of the simulation
        :param agents: list of agents to collect data from
        :param current_generation: current generation number
        """
        for agent in agents:
            self.collect_fitness(agent, elapsed_time, evaluate=False)
            self.collect_fitness(agent, elapsed_time, evaluate=False, new_generation=True)
        self.generation_intervals[-1].close(elapsed_time)
        self.generation_intervals.append(Interval(elapsed_time, current_generation))

    def save_data(self, elapsed_time):
        """
        Save the data collected by the DataCollector.
        :param elapsed_time: elapsed time of the simulation
        """
        self._save_data_for_graphics()
        self._save_generation_intervals(elapsed_time)

    def _update_fitness(self, car_id, elapsed_time, fitness_score):
        self._update_total_fitness(car_id, elapsed_time, fitness_score)

    @staticmethod
    def _save_fitness_data(fitness_data_list, filename='assets/data_files/results/fitness_data.csv'):
        # Sort the data by fitness score in descending order
        sorted_fitness_data = sorted(fitness_data_list, key=lambda x: x['fitness_score'], reverse=True)

        # Write the data to a CSV file
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Fitness Score', 'Car Position'])

            for data in sorted_fitness_data:
                writer.writerow([data['fitness_score'], data['tile']])

    def _update_total_fitness(self, car_id, elapsed_time, fitness):
        elapsed_time = round(elapsed_time, 3)
        if car_id not in self.total_fitness_per_car_through_time:
            self.total_fitness_per_car_through_time[car_id] = {}
        self.total_fitness_per_car_through_time[car_id][elapsed_time] = fitness

    def _save_fitness_scores(self, filename='assets/data_files/results/total_fitness_scores.json'):
        with open(filename, 'w') as file:
            json.dump(self.total_fitness_per_car_through_time, file, indent=4)

    def _save_generation_intervals(self, elapsed_time, filename='assets/data_files/results/generation_intervals.json'):
        elapsed_time = round(elapsed_time, 3)
        self.generation_intervals[-1].close(elapsed_time)
        intervals_data = [{'start': round(interval.start, 3), 'end': round(interval.end, 3)} for interval in
                          self.generation_intervals]
        with open(filename, 'w') as file:
            json.dump(intervals_data, file, indent=4)

    def _save_data_for_graphics(self):
        self._save_fitness_scores()
        self.save_top_fitness()

    def add_top_fitness(self, top_fitness):
        """
        Add the top fitness of the generation to the list.
        :param top_fitness: top fitness of the generation
        """
        self.top_fitness_per_generation.append(top_fitness)

    def save_top_fitness(self):
        """
        Save the top fitness of each generation to a JSON file.
        """
        with open('assets/data_files/results/top_fitness.json', 'w') as f:
            json.dump(self.top_fitness_per_generation, f)
