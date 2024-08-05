class FishingCatch:
    def __init__(self):
        self.catches = []

    def add_item(self, fish):
        self.catches.append(fish)

    def total_item_count(self):
        return sum(number for _, number in self.catches)

    def show_item(self):
        return self.catches
