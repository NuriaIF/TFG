class GenerationCreator:
    def __init__(self, population_size, chromosome_size):
        self.population_size = population_size
        self.chromosome_size = chromosome_size

    def create_generation(self):
        return [Chromosome(self.chromosome_size) for _ in range(self.population_size)]