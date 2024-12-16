import random
from relics import all_relics

class CombatInterface:
    def __init__(self, player, encounter):
        self.player = player
        self.encounter = encounter
        print("Combat started!")
        print(f"Player: {self.player.name} ({self.player.id})")
        print(f"Encounter: {[f'{monster.name} ({monster.id})' for monster in self.encounter]}")

class World:
    def __init__(self, seed, ascension_level=20):
        self.ascension_level = ascension_level
        self.act_layout = []  # This can be a list of acts, each act containing a list of floors
        self.floor_number = 0
        self.current_act = 0
        self.seed = seed
        self.relic_list = {
            "boss": [],
            "rare": [],
            "uncommon": [],
            "common": []
        }
        self.potion_chance = 0.2
        random.seed(seed)
        
        # Generate the relic list and act layout upon world creation
        self.generate_relic_list(all_relics)
        self.generate_act_layout()

    def add_act(self, act):
        self.act_layout.append(act)

    def next_floor(self, player):
        if self.current_act < len(self.act_layout):
            act = self.act_layout[self.current_act]
            if self.floor_number < len(act):
                current_floor = act[self.floor_number]
                print(f"Entering floor {self.floor_number + 1} of Act {self.current_act + 1}: {current_floor}")
                if current_floor == "Combat":
                    encounter = self.generate_encounter()
                    CombatInterface(player, encounter)
                self.floor_number += 1
                if self.floor_number == len(act):
                    self.current_act += 1
                    self.floor_number = 0
                    if self.current_act < len(self.act_layout):
                        print(f"Entering Act {self.current_act + 1}")
            else:
                print("No more floors in the current act.")
        else:
            print("No more acts available.")

    def generate_relic_list(self, all_relics):
        """
        Generates the relic list based on the seed.
        
        :param all_relics: A dictionary containing all relics categorized by rarity.
        """
        for rarity, relics in all_relics.items():
            random.shuffle(relics)
            self.relic_list[rarity] = relics

    def add_relic(self, rarity, relic):
        if rarity in self.relic_list:
            self.relic_list[rarity].append(relic)
        else:
            print(f"Ungültige Seltenheit: {rarity}")

    def generate_act_layout(self):
        """
        Generates the layout for three acts, each containing 16 normal floors and a boss floor.
        For now, only combat rooms will appear.
        """
        room_types = ["Combat", "Rest Site", "Elite Fight", "Shop", "Question Mark"]
        room_chances = [1.0, 0.0, 0.0, 0.0, 0.0]  # Only combat rooms have a chance to appear

        for act_number in range(3):
            act = []
            for floor_number in range(16):
                room = random.choices(room_types, weights=room_chances, k=1)[0]
                act.append(room)
            act.append("Boss")
            self.add_act(act)

    def generate_encounter(self):
        """
        Generates a random encounter based on the current act.
        """
        encounters = {
            0: [("Monster001", "Goblin", 50), ("Monster002", "Orc", 60)],  # Act 1 encounters
            1: [("Monster003", "Troll", 70), ("Monster004", "Golem", 80)],  # Act 2 encounters
            2: [("Monster005", "Dragon", 90), ("Monster006", "Demon", 100)]  # Act 3 encounters
        }
        act_encounters = encounters.get(self.current_act, [])
        selected_encounter = random.choice(act_encounters)
        return [MonsterCharacter(monster_id, name, hp) for monster_id, name, hp in [selected_encounter]]

class Character:
    def __init__(self, character_id, name, max_hp):
        self.id = character_id
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.buffs = []
        self.debuffs = []

    def take_damage(self, amount):
        """
        Verursacht Schaden beim Charakter. HP können nicht unter 0 fallen.
        
        :param amount: Die Höhe des Schadens.
        """
        self.current_hp = max(0, self.current_hp - amount)
        print(f"{self.name} ({self.id}) nimmt {amount} Schaden! HP: {self.current_hp}/{self.max_hp}")

    def heal(self, amount):
        """
        Heilt den Charakter. HP können nicht über das Maximum hinausgehen.
        
        :param amount: Die Höhe der Heilung.
        """
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        print(f"{self.name} ({self.id}) heilt sich um {amount} HP! HP: {self.current_hp}/{self.max_hp}")

    def add_buff(self, buff):
        self.buffs.append(buff)
        print(f"{self.name} ({self.id}) erhält den Buff: {buff}")

    def remove_buff(self, buff):
        if buff in self.buffs:
            self.buffs.remove(buff)
            print(f"{self.name} ({self.id}) verliert den Buff: {buff}")
        else:
            print(f"{self.name} ({self.id}) hat den Buff {buff} nicht.")

    def add_debuff(self, debuff):
        self.debuffs.append(debuff)
        print(f"{self.name} ({self.id}) erhält den Debuff: {debuff}")

    def remove_debuff(self, debuff):
        if debuff in self.debuffs:
            self.debuffs.remove(debuff)
            print(f"{self.name} ({self.id}) verliert den Debuff: {debuff}")
        else:
            print(f"{self.name} ({self.id}) hat den Debuff {debuff} nicht.")

class PlayerCharacter(Character):
    def __init__(self, player_id, name, max_hp):
        super().__init__(player_id, name, max_hp)
        self.current_potions = []
        self.max_potion_number = 5
        self.relics = []

    def add_potion(self, potion):
        if len(self.current_potions) < self.max_potion_number:
            self.current_potions.append(potion)
        else:
            print("Du kannst keine weiteren Tränke aufnehmen!")

    def use_potion(self, potion_index):
        if 0 <= potion_index < len(self.current_potions):
            potion = self.current_potions.pop(potion_index)
            print(f"Du benutzt {potion}.")
        else:
            print("Ungültiger Trankindex!")

    def add_relic(self, relic):
        self.relics.append(relic)
        print(f"Du hast ein neues Relikt erhalten: {relic}")

class MonsterCharacter(Character):
    def __init__(self, monster_id, name, max_hp):
        super().__init__(monster_id, name, max_hp)
        self.intent = None
        self.move_list = ["Attack", "Defend", "Heal"]
        self.current_move_index = 0

    def get_next_move(self):
        """
        Gibt den nächsten Zug des Monsters zurück und aktualisiert den aktuellen Zugindex.
        """
        if self.move_list:
            move = self.move_list[self.current_move_index]
            self.current_move_index = (self.current_move_index + 1) % len(self.move_list)
            return move
        else:
            return None

# Beispiel für die Erstellung einer Welt
welt = World(seed=12345)

# Beispiel für die Erstellung eines Spielercharakters
spieler = PlayerCharacter(player_id="Hero001", name="Hero", max_hp=80)

# Beispiel für den Übergang zum nächsten Stockwerk
welt.next_floor(spieler)
welt.next_floor(spieler)
welt.next_floor(spieler)