import random
from monsters import *
from player import *

class CombatInterface:
    def __init__(self, player, encounter,world, round=1):
        self.player = player
        self.encounter = encounter
        self.round = round
        self.world = world
        self.out_print = world.out_print
        self.persistent_buffs = ["Barricade", "Ritual","Curl Up","Strength"]
        self.persistent_debuffs = []
        self.phase ="Begin Round"   
        
        if self.out_print:
            print("Combat started!")
            print(f"Player: {self.player.name} ({self.player.id})")
            print(f"Encounter: {[f'{monster.name} ({monster.id})' for monster in self.encounter]}")

    def start_combat(self):

        self.player.clear_events()
        for relic in self.player.relics:            
            relic.effect(self.player)

        self.player.begin_combat()

    def end_combat(self):
        
        self.player.end_combat()
        self.trigger_events(self.player.events["on_combat_end"])
        if self.out_print:
            print("All monsters have been defeated!")
        self.world.situation = "Next Floor"
        self.world.next_floor()

    def manage_round(self):
        #Berechne alles bis der Spieler dran ist
        while self.phase != "Player Turn":
            if (self.phase == "Begin Round"):
                if self.out_print:
                    print(f"\nRound {self.round}")

                for character in [self.player] + self.encounter:
                    self.trigger_events(character.events["on_turn_start"],0,0,0)

                self.manage_character_block(self.player)
                self.determine_monster_moves()
                self.phase = "Player Turn"
                self.player.draw(5)
                self.player.energy = self.player.max_energy
            elif (self.phase == "Player Turn"):
                
                self.player_turn()

            elif (self.phase == "Monster Turn"):
                self.player.discard_hand()
                self.manage_character_buffs_debuffs(self.player)
                for monster in self.encounter:
                    self.manage_character_block(monster)
                self.monster_turn()
                for monster in self.encounter:
                    self.manage_character_buffs_debuffs(monster)
                if self.out_print:
                    print(f"\nRound {self.round} ends!")
                self.trigger_events(self.player.events["on_turn_end"],0,0,0)
                self.round += 1
                self.phase = "Begin Round"

    def manage_character_block(self, character):
        # Block verwalten
        if "Barricade" not in character.buffs:
            character.block = 0


    def manage_character_buffs_debuffs(self, character):

        # Buffs verwalten
        buffs_to_remove = []
        buffs_copy = character.buffs.copy()  # Kopie des Wörterbuchs erstellen, da es sonst während des Iterierens verändert wird
    
        for buff_name, buff_value in buffs_copy.items():
            if buff_name not in self.persistent_buffs:
                character.buffs[buff_name] -= 1
                if character.buffs[buff_name] <= 0:
                    buffs_to_remove.append(buff_name)

        for buff_name in buffs_to_remove:
            character.remove_buff(buff_name)

        # Debuffs verwalten
        debuffs_to_remove = []
        for debuff_name, debuff_value in character.debuffs.items():
            character.debuffs[debuff_name] -= 1
            if character.debuffs[debuff_name] <= 0:
                debuffs_to_remove.append(debuff_name)
        for debuff_name in debuffs_to_remove:
            character.remove_debuff(debuff_name)

    def determine_monster_moves(self):
        for monster in self.encounter:
            if monster.current_hp > 0:
                monster.get_next_move()
                moves = monster.next_move
                for move in moves:
                    if isinstance(move, AttackMove):
                        movedamage = self.player.calculate_damage(move.damage,monster)
                        if self.out_print:
                            print(f"{monster.name} intends to use {move.intent} dealing {movedamage} damage.")
                    else:
                        if self.out_print:
                            print(f"{monster.name} intends to use {move.intent}.")


    def player_turn(self):
        if self.out_print:
            print(f"{self.player.name}'s turn!")
        if self.out_print:
            print(self.world.get_State())
        """ 
        # Autoplay für Testzwecke
        if self.world.autoplay:
            while self.player.energy > 0 or all(monster.current_hp < 0 for monster in self.encounter) or self.player.hand == []:
                print(f"{self.player.name}'s energy: {self.player.energy}")
                self.player.print_hand()
                self.player.print_draw_pile()
                self.player.print_discard_pile()
                print(f"Exhausted: {self.player.exhausted}")
                print(f"Block: {self.player.block}")
                print(f"HP: {self.player.current_hp}/{self.player.max_hp}")
                print(f"Monsters: {[f'{monster.name} ({monster.id})' for monster in self.encounter]}")
                card_index = 0
                if 0 <= card_index < len(self.player.hand):
                    card = self.player.hand[card_index]
                    #Wenn die Karte target enemy hat und es mehr als einen gegner gibt, muss der Spieler einen Gegner auswählen
                    if card.needs_target: 
                        if len(self.encounter) > 1:
                            for i, monster in enumerate(self.encounter):
                                if monster.current_hp > 0:
                                    target_index=i
                                    break
                            if 0 <= target_index < len(self.encounter):
                                target = self.encounter[target_index]
                                card.play(self.player, target)
                            else:
                                print("Invalid target index!")
                        else:
                            card.play(self.player, self.encounter[0])
                    else:
                        card.play(self.player, None)
                else:
                    print("Invalid card index!")
                print("\n")

        # Spielerzug
        else:
            while True:
                print(f"{self.player.name}'s energy: {self.player.energy}")
                self.player.print_hand()
                self.player.print_draw_pile()
                self.player.print_discard_pile()
                print(f"Exhausted: {self.player.exhausted}")
                print(f"Block: {self.player.block}")
                print(f"HP: {self.player.current_hp}/{self.player.max_hp}")
                print(f"Monsters: {[f'{monster.name} ({monster.id})' for monster in self.encounter]}")
                print("Choose a card to play:")
                card_index = input()
                if card_index == "e":
                    break
                card_index = int(card_index)
                if 0 <= card_index < len(self.player.hand):
                    card = self.player.hand[card_index]
                    #Wenn die Karte target enemy hat und es mehr als einen gegner gibt, muss der Spieler einen Gegner auswählen
                    if card.needs_target: 
                        if len(self.encounter) > 1:
                            print("Choose a target:")
                            for i, monster in enumerate(self.encounter):
                                print(f"{i}: {monster}")
                            target_index = int(input())
                            if 0 <= target_index < len(self.encounter):
                                target = self.encounter[target_index]
                                card.play(self.player, target)
                            else:
                                print("Invalid target index!")
                        else:
                            card.play(self.player, self.encounter[0])
                    else:
                        card.play(self.player, None)
                else:
                    print("Invalid card index!")
                print("\n")

        """
        

    def trigger_events(self, events, *args, **kwargs):
        for event in events:
            if self.out_print:
                print(f"Triggering event: {event}")
            event(*args, **kwargs)


    def monster_turn(self):
        for monster in self.encounter:
            if monster.current_hp > 0:
                for m in monster.next_move:
                    if isinstance(m, BuffMove):
                        if m.target == "self":
                            monster.add_buff(m.buff_name, m.buff_value)
                        if m.target == "allies":
                            for ally in self.encounter:
                                ally.add_buff(m.buff_name, m.buff_value)
                    elif isinstance(m, DebuffMove):
                        self.player.add_debuff(m.debuff_name, m.debuff_value)
                    elif isinstance(m, AttackMove):
                        self.player.take_damage(m.damage,monster,m)
                    elif isinstance(m, BlockMove):
                        monster.add_block(m.block_value)
                    elif isinstance(m, StatusMove):
                        self.player.add_temp_card(m.statusname,m.position,m.statusnumber)
                
                if self.player.current_hp <= 0:
                    if self.out_print:
                        print(f"{self.player.name} has been defeated!")
                    break

class World:
    def __init__(self, seed, ascension_level=20,autoplay=False,spieler="Ironclad",out_print=False):
        self.ascension_level = ascension_level
        self.act_layout = []  # This can be a list of acts, each act containing a list of floors
        self.floor_number = 0
        self.current_act = 0
        self.seed = seed
        if spieler == "Ironclad":
            self.player = Ironclad(out_print)
        self.out_print = out_print
        self.combat = None
        self.autoplay = autoplay
        self.reward = 0
        self.relic_list = {
            "boss": [],
            "rare": [],
            "uncommon": [],
            "common": []
        }
        self.actionspace=[]
        #soll beschreiben in welcher Situation sich der Spieler befindet (Kampf, Event, Shop, Rest, Auswahlmenü, etc.)
        self.situation = "Creating World"
        self.potion_chance = 0.2
        random.seed(seed)
        if self.out_print:
            print(f"Seed: {seed}")
        
        # Generate the relic list and act layout upon world creation
        self.generate_relic_list(all_relics)
        self.generate_act_layout()
        #start the first combat
        self.next_floor()

    def add_act(self, act):
        self.act_layout.append(act)


    def next_floor(self):
        #grundsärzlich wird der nächste Floor aufgerufen für den moment wird nur einfach ein neuer Combat aufgerufen

        # als basis wird einfach für jeden neuen Floor ein reward von 20 vergeben, außer wenn es der erste Floor ist
        if self.floor_number != 0:
            self.update_reward(20)
        if self.out_print:
            print(self.get_reward())

        # Reset the combat interface
        self.combat = None


        encounter = self.generate_encounter()
        self.combat = CombatInterface(self.player, encounter,self)
        self.floor_number += 1
        self.situation = "Combat"
        self.combat.start_combat()
        self.combat.manage_round()

        '''
        
        if self.current_act < len(self.act_layout):
            act = self.act_layout[self.current_act]
            if self.floor_number < len(act):
                current_floor = act[self.floor_number]
                print(f"Entering floor {self.floor_number + 1} of Act {self.current_act + 1}: {current_floor}")
                if current_floor == "Combat":
                    encounter = self.generate_encounter()
                    self.combat = CombatInterface(self.player, encounter,self)
                    self.combat.start_combat()
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
        '''

    def generate_relic_list(self, all_relics):
        """
        Generates the relic list based on the seed.
        
        :param all_relics: A dictionary containing all relics categorized by rarity.
        """"""
        for rarity, relics in all_relics.items():
            random.shuffle(relics)
            self.relic_list[rarity] = relics
        """
        

    def add_relic(self, rarity, relic):
        if rarity in self.relic_list:
            self.relic_list[rarity].append(relic)
        else:
            if self.out_print:
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
            0: [
                (["Cultist"], 25),
                (["Jaw Worm"], 25),
                (["Louse", "Louse"], 25),
                (["Acid Slime (M)", "Acid Slime (S)"], 25)
            ]
        }
        act_encounters = encounters.get(self.current_act, [])
        if not act_encounters:
            return []

        selected_encounter = random.choices(act_encounters, weights=[chance for _, chance in act_encounters], k=1)[0]
        return self.create_monsters(selected_encounter[0])

    def create_monsters(self, monster_names):
        """
        Creates monsters based on the provided list of monster names.
        """
        random.seed(self.seed)
        monsters = []
        for name in monster_names:
            self.increment_seed()
            if name == "Cultist":
                monsters.append(Cultist(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Jaw Worm":
                monsters.append(JawWorm(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Louse":
                monsters.append(RedLouse(f"Monster{self.seed}", self.seed,self.out_print) if random.random() < 0.5 else GreenLouse(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Red Louse":
                monsters.append(RedLouse(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Green Louse":
                monsters.append(GreenLouse(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Slime (M)":
                monsters.append(AcidSlimeM(f"Monster{self.seed}", self.seed,self.out_print) if random.random() < 0.5 else SpikeSlimeM(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Slime (S)":
                monsters.append(AcidSlimeS(f"Monster{self.seed}", self.seed,self.out_print) if random.random() < 0.5 else SpikeSlimeS(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Acid Slime (M)":
                monsters.append(AcidSlimeM(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Acid Slime (S)":
                monsters.append(AcidSlimeS(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Spike Slime (M)":
                monsters.append(SpikeSlimeM(f"Monster{self.seed}", self.seed,self.out_print))
            elif name == "Spike Slime (S)":
                monsters.append(SpikeSlimeS(f"Monster{self.seed}", self.seed,self.out_print))
        return monsters

    def increment_seed(self):
        """
        Increments the seed by 1.
        """
        self.seed += 1

    def check_combat_ended(self):

        #check if player is dead
        if self.player.current_hp <= 0:
            if self.out_print:
                print(f"{self.player.name} has been defeated!")
            self.situation = "Game Over"
        
        #check if all monsters are dead
        if all(monster.current_hp <= 0 for monster in self.combat.encounter):
            self.combat.end_combat()


    def update_reward(self, reward):
        self.reward += reward


    def get_reward(self):
        return self.reward

    def get_state_human(self):
        #Soll den Kompletten State des Spiels zurückgeben menschenlesbar
        print("--------------------")
        worldstate = {
            "seed": self.seed,
            "ascension_level": self.ascension_level,
            #"act_layout": self.act_layout,
            "floor_number": self.floor_number,
            #"current_act": self.current_act,
            #"potionchance": self.potion_chance
            "situation": self.situation
        }
        print("Worldstate:")
        for key, value in worldstate.items():
            print(f"{key}: {value}")
        #ursprüngliche version wo ich alles mitgenommen hatte
        playerstate = {
            "player": self.player.get_State()[0]
        }

        #Bei dem Playerstate soll nur curr hp und max hp zurückgegeben werden, 
        # die namen der relics sowie die Karten in der Hand dann im Deck und im Discard Pile
        
        playerstate = {
            "current_hp": self.player.current_hp,
            "max_hp": self.player.max_hp,
            "energy": self.player.energy,
            "block": self.player.block,
            "relics": [relic.name for relic in self.player.relics],
            "hand": [card.name for card in self.player.hand],
            "draw_pile": [card.name for card in self.player.draw_pile],
            "discard_pile": [card.name for card in self.player.discard_pile],
            "current_card_playing": self.player.currentcardplaying.name if self.player.currentcardplaying else None
        }
        print("Playerstate:")
        for key, value in playerstate.items():
            if value!=None:
                print(f"{key}: {value}")
        #alte version die alles ausgibt
        encounterstate = {
            "encounter": [monster.get_State()[0] for monster in self.combat.encounter]
        }

        #neue version die nur die hp und den namen ausgibt
        encounterstate = {
            "encounter": [
                {
                    "name": monster.name,
                    "current_hp": monster.current_hp,
                    "max_hp": monster.max_hp,
                    "next_move": monster.next_move[0].name if monster.next_move else None,
                    "block": monster.block
                }
                for monster in self.combat.encounter
            ]
        }
        print("Encounterstate:")
        for monster in encounterstate["encounter"]:
            print(monster)
        return [worldstate,playerstate,encounterstate]
    
    def get_state_machinereadble(self):
        #Soll den Kompletten State des Spiels zurückgeben maschinenlesbar
        situations = {
            "Creating World": 0,
            "Combat": 1,
            "Choose Card Target": 2,
            "Next Floor": 3,
            "Game Over": 4,
        }

        '''
            "Rest Site": 5,
            "Elite Fight": 6,
            "Shop": 7,
            "Question Mark": 8,
            "Boss": 9
        '''
        situation_to_one_hot = {name: [1 if i == idx else 0 for i in range(situations.__len__())] for idx, name in enumerate(situations.keys())}

        worldstate_maschinereadable = [
            #self.act_layout,
            #self.current_act,
            #self.potion_chance,
            self.floor_number
            
        ]+situation_to_one_hot.get(self.situation, [0] * situations.__len__())

        playerstate_maschinereadable = self.player.get_State()[1]

        def pad_monsters(encounter, max_length=2):
            monsteranzahl = len(encounter)
            padded_monster = []
            for monster in encounter:
                padded_monster+=monster.get_State()[1] 
            leeres_monster=globals()["NothingMonster"](self.out_print)
            while monsteranzahl < max_length:
                padded_monster+=leeres_monster.get_State()[1]  # leeres Monster hinzufügen
                monsteranzahl += 1
            return padded_monster
        
        encounterstate_maschinereadable = pad_monsters(self.combat.encounter)
        return worldstate_maschinereadable+playerstate_maschinereadable+encounterstate_maschinereadable
    
    def get_entire_action_space(self):
        #Soll den gesamten möglichen Actionspace zurückgeben
        actionspace = ["End Turn","Play card:1","Play card:2","Play card:3","Play card:4","Play card:5","Target Monster:1","Target Monster:2"]
        return actionspace
    
    def get_action_space(self):
        #Soll die möglichen Aktionen des Spielers zurückgeben, in einem Array wobei jede Aktion ein
        #String ist der die Aktion beschreibt
        self.actionspace = []
        if self.situation == "Combat":
            self.actionspace.append("End Turn")
            #gehe jede Karte in deiner Hand durch und füge sie dem actionspace hinzu, wenn du genug Energie hast
            card_index = 0
            for card in self.player.hand:
                card_index += 1
                if card.cost <= self.player.energy:
                    self.actionspace.append("Play card:"+str(card_index))
        if self.situation == "Choose Card Target":
            monster_index = 0
            for monster in self.combat.encounter:
                monster_index += 1
                if monster.current_hp > 0:
                    self.actionspace.append("Target Monster:"+str(monster_index))
        return self.actionspace


    def take_action(self,action):

        self.get_action_space()

        if self.out_print:
            print("Taking action: ", action)
        if self.out_print:
            print("erlaubte Aktionen:",self.actionspace)

        if action not in self.actionspace:
            self.update_reward(-1)
            #print("Invalid action")
            return

        if self.situation == "Combat":

            if action == "End Turn":
                #negativer reward für das beenden des Zuges, wenn der Spieler noch energy hat
                self.update_reward(-self.player.energy)
                self.combat.phase = "Monster Turn"
                self.combat.manage_round()
            if action.startswith("Play card:"):
                card_index = int(action.split(":")[1])-1
                card = self.player.hand[card_index]
                #Karte aus der Hand entfernen und in currentcardplaying speichern
                self.player.hand.remove(card)
                self.player.currentcardplaying = card

                #reward dafür eine Karte zu spielen
                self.update_reward(1)

                #Wenn die Karte target enemy hat und es mehr als einen gegner gibt, muss der Spieler einen Gegner auswählen
                if card.needs_target(): 
                    if len(self.combat.encounter) > 1:
                        self.situation = "Choose Card Target"
                    else:
                        card.play(self.player, self.combat.encounter[0])
                else:
                    card.play(self.player, None)
            self.check_combat_ended()
                
        if self.situation == "Choose Card Target":
            if action.startswith("Target Monster:"):
                #reward dafür ein Ziel auszuwählen
                self.update_reward(2)

                monster_index = int(action.split(":")[1])-1
                target = self.combat.encounter[monster_index]
                self.player.currentcardplaying.play(self.player, target)
                self.situation = "Combat"
                self.check_combat_ended()
