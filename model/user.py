class User:
    def __init__(self, user_id, name, coins,diamonds,fish_inventory,rod_type,level,current_experience,experience_for_next_level):
        self.user_id = user_id
        self.name = name
        self.rod_type = rod_type
        self.inventory = UserInventory(coins,diamonds,fish_inventory)
        self.progress = UserProgress(level,current_experience,experience_for_next_level)
class UserInventory:
    def __init__(self,coins,diamonds,fish_inventory):
        self.coins = coins
        self.diamonds = diamonds
        self.fish_inventory = fish_inventory

class UserProgress:
    def __init__(self,level,current_experience,experience_for_next_level):
        self.level = 1
        self.current_experience = 0
        self.experience_for_next_level = 100

