import random
from character import *

class Move:
    def __init__(self, name, intent):
        self.name = name
        self.intent = intent

class AttackMove(Move):
    def __init__(self, name, damage,intent="Attack"):
        super().__init__(name, intent)
        self.damage = damage

class BuffMove(Move):
    def __init__(self, name, buff_name, buff_value,target="self", intent="Buff"):
        super().__init__(name, intent)
        self.buff_name = buff_name
        self.buff_value = buff_value
        self.target = target

class DebuffMove(Move):
    def __init__(self, name, debuff_name, debuff_value, intent="Debuff"):
        super().__init__(name, intent)
        self.debuff_name = debuff_name
        self.debuff_value = debuff_value


class StatusMove(Move):
    def __init__(self, name, statusname, statusnumber, intent="Debuff",position="Discard Pile"):
        super().__init__(name, intent)
        self.statusname = statusname
        self.statusnumber = statusnumber
        self.position = position

class BlockMove(Move):
    def __init__(self, name, block_value, intent="Block"):
        super().__init__(name, intent)
        self.block_value = block_value


class MonsterCharacter(Character):
    def __init__(self, monster_id, name, max_hp,out_print):
        super().__init__(monster_id, name, max_hp,out_print)
        self.intent = None
        # Liste von Moves, die das Monster ausführen kann, wird für jedes Monster selbst definiert
        self.movelist = []
        # Nächster Move, der ausgeführt wird
        self.next_move=None
        # Index des Nächsten Moves in der movelist
        self.next_move_index = 0

    def __str__(self):
        # Gibt den Namen des Monsters und seine aktuelle HP zurück.
        return self.name + f" ({self.current_hp}/{self.max_hp})"

    def get_next_move(self):
        """
        Gibt den nächsten Zug des Monsters zurück und aktualisiert den aktuellen Zugindex.
        """
        if self.movelist:
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]
        else:
            return None
        
        
    def monster_name_to_vector(self):
        monster_names=["Nothing","Cultist","Red Louse","Green Louse","Jaw Worm","Acid Slime (M)","Acid Slime (S)","Spike Slime (M)","Spike Slime (S)"]
        vektorspace=monster_names.__len__()
        name=self.name
        # Erstellen von One-Hot-Encodings für Monsternamen , gibt bis zu 80 verschiedene Monster
        monster_name_to_one_hot = {name: [1 if i == idx else 0 for i in range(vektorspace)] for idx, name in enumerate(monster_names)}
        return monster_name_to_one_hot.get(name, [0] * vektorspace)

        
    def get_State(self):
        state = {
            "name": self.name,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "next_move_index": self.next_move_index,
            "next_move": self.next_move
        }

        maschinereadablestate = [
            self.current_hp,
            self.next_move_index
        ]+self.monster_name_to_vector()
        return state, maschinereadablestate

class NothingMonster(MonsterCharacter):
    def __init__(self,out_print):
        super().__init__(monster_id=0, name="Nothing", max_hp=0,out_print=out_print)

    def get_next_move(self):
        return None

class Cultist(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(50, 56)
        super().__init__(monster_id=id, name="Cultist", max_hp=hp,out_print=out_print)
        self.ritual_applied = False
        self.movelist = [
            [BuffMove(name="Incantation", buff_name="Ritual", buff_value=5)],
            [AttackMove(name="Dark Strike",damage=6)]
        ]

    def get_next_move(self):
        """
        Gibt den nächsten Zug des Monsters zurück und aktualisiert den aktuellen Zugindex.
        """
        if not self.ritual_applied:
            self.ritual_applied = True
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]
        else:
            self.next_move_index = 1
            self.next_move=self.movelist[self.next_move_index]

class RedLouse(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(13, 16)
        super().__init__(monster_id=id, name="Red Louse", max_hp=hp,out_print=out_print)
        self.add_buff("Curl Up", random.randint(9, 12))
        self.damage = random.randint(5, 7)
        self.last_intent = None
        self.bite_count = 0
        self.movelist = [
            [BuffMove("Grow", "Strength", 4)],
            [AttackMove("Bite", 6)]
        ]

    def get_next_move(self):
        """
        Determines the next move for the Red Louse.
        """
        if self.last_intent == "Grow":
            self.last_intent = "Bite"
            self.bite_count += 1            
            self.next_move_index = 1
            self.next_move=self.movelist[self.next_move_index]
        elif self.bite_count >= 2:
            self.last_intent = "Grow"
            self.bite_count = 0
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]
        else:
            if random.random() < 0.25:
                self.last_intent = "Grow"
                self.bite_count = 0
                self.next_move_index = 0
                self.next_move=self.movelist[self.next_move_index]
            else:
                self.last_intent = "Bite"
                self.bite_count += 1
                self.next_move_index = 1
                self.next_move=self.movelist[self.next_move_index]

class GreenLouse(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(12, 18)
        super().__init__(monster_id=id, name="Green Louse", max_hp=hp,out_print=out_print)
        self.add_buff("Curl Up", random.randint(9, 12))
        self.damage = random.randint(5, 7)
        self.last_intent = None
        self.bite_count = 0
        self.movelist = [
            [AttackMove("Bite", 6)],
            [DebuffMove("Spit Web", "Weak", 2)]
        ]

    def get_next_move(self):
        """
        Determines the next move for the Green Louse.
        """
        if self.last_intent == "Spit Web":
            self.last_intent = "Bite"
            self.bite_count += 1
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]
        elif self.bite_count >= 2:
            self.last_intent = "Spit Web"
            self.bite_count = 0
            self.next_move_index = 1
            self.next_move=self.movelist[self.next_move_index]
        else:
            if random.random() < 0.5:
                self.last_intent = "Bite"
                self.bite_count += 1
                self.next_move_index = 0
                self.next_move=self.movelist[self.next_move_index]
            else:
                self.last_intent = "Spit Web"
                self.bite_count = 0
                self.next_move_index = 1
                self.next_move=self.movelist[self.next_move_index]

class JawWorm(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(42, 46)
        super().__init__(monster_id=id, name="Jaw Worm", max_hp=hp,out_print=out_print)
        self.last_move = None
        self.thrash_count = 0
        self.movelist = [
            [AttackMove(name="Chomp", damage=12)],
            [AttackMove(name="Thrash", damage=7), BlockMove(name="Thrash",block_value=5)],
            [BuffMove(name="Bellow", buff_name="Strength", buff_value=5), BlockMove(name="Bellow", block_value=9)]
        ]

    def get_next_move(self):
        """
        Determines the next move for the Jaw Worm.
        """
        if self.last_move is None:
            self.last_move = "Chomp"
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]

        possible_moves = []
        if self.last_move != "Bellow":
            possible_moves.append("Bellow")
        if self.thrash_count < 2:
            possible_moves.append("Thrash")
        if self.last_move != "Chomp":
            possible_moves.append("Chomp")

        next_move = random.choices(
            possible_moves,
            weights=[0.45 if move == "Bellow" else 0.30 if move == "Thrash" else 0.25 for move in possible_moves],
            k=1
        )[0]

        if next_move == "Thrash":
            self.thrash_count += 1
        else:
            self.thrash_count = 0

        self.last_move = next_move
        
        #schaue an welcher stelle im array der move den namen hat und setze den index auf diese stelle
        for i in range(len(self.movelist)):
            if self.movelist[i][0].name == next_move:
                self.next_move_index = i
                break
        self.next_move=self.movelist[self.next_move_index]

class AcidSlimeM(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(29, 35)
        super().__init__(monster_id=id, name="Acid Slime (M)", max_hp=hp,out_print=out_print)
        self.last_move = None
        self.corrosive_spit_count = 0
        self.tackle_count = 0
        self.movelist = [
            [AttackMove(name="Corrosive Spit", damage=8,intent="AttackDebuff"), StatusMove(name="Corrosive Spit",  statusname="Slimed",statusnumber=1)],
            [DebuffMove(name="Lick", debuff_name="Weak", debuff_value=1)],
            [AttackMove(name="Tackle", damage=12)]
        ]

    def get_next_move(self):
        """
        Determines the next move for the Acid Slime (M).
        """
        possible_moves = []
        if self.last_move != "Lick":
            possible_moves.append("Lick")
        if self.corrosive_spit_count < 2:
            possible_moves.append("Corrosive Spit")
        if self.tackle_count < 2:
            possible_moves.append("Tackle")

        next_move = random.choices(
            possible_moves,
            weights=[0.20 if move == "Lick" else 0.40 for move in possible_moves],
            k=1
        )[0]

        if next_move == "Corrosive Spit":
            self.corrosive_spit_count += 1
            self.tackle_count = 0
        elif next_move == "Tackle":
            self.tackle_count += 1
            self.corrosive_spit_count = 0
        else:
            self.corrosive_spit_count = 0
            self.tackle_count = 0

        self.last_move = next_move
        
        #schaue an welcher stelle im array der move den namen hat und setze den index auf diese stelle
        for i in range(len(self.movelist)):
            if self.movelist[i][0].name == next_move:
                self.next_move_index = i
                break  
        self.next_move=self.movelist[self.next_move_index]
    
class AcidSlimeS(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(9, 13)
        super().__init__(monster_id=id, name="Acid Slime (S)", max_hp=hp,out_print=out_print)
        self.movelist = [
            [DebuffMove(name="Lick", debuff_name="Weak", debuff_value=1)],
            [AttackMove(name="Tackle", damage=4)]
        ]
        self.next_move_index = 0
        self.last_move = None

    def get_next_move(self):
        """
        Determines the next move for the Acid Slime (S).
        """
        if self.last_move is None:
            self.last_move = "Lick"
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]

        if self.last_move == "Lick":
            self.last_move = "Tackle"
            self.next_move_index = 1
            self.next_move=self.movelist[self.next_move_index]
        
        else:
            self.last_move = "Lick"
            self.next_move_index = 0
            self.next_move=self.movelist[self.next_move_index]
            
class SpikeSlimeM(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(29, 34)
        super().__init__(monster_id=id, name="Spike Slime (M)", max_hp=hp,out_print=out_print)
        self.last_move = None
        self.flame_tackle_count = 0
        self.movelist = [
            [AttackMove(name="Flame Tackle", damage=10), DebuffMove(name="Flame Tackle", debuff_name="Slimed", debuff_value=1)],
            [DebuffMove(name="Lick", debuff_name="Frail", debuff_value=1)]
        ]

    def get_next_move(self):
        """
        Determines the next move for the Spike Slime (M).
        """
        possible_moves = []
        if self.last_move != "Lick":
            possible_moves.append("Lick")
        if self.flame_tackle_count < 2:
            possible_moves.append("Flame Tackle")

        next_move = random.choices(
            possible_moves,
            weights=[0.50 if move == "Lick" else 0.50 for move in possible_moves],
            k=1
        )[0]

        if next_move == "Flame Tackle":
            self.flame_tackle_count += 1
        else:
            self.flame_tackle_count = 0

        self.last_move = next_move
        #schaue an welcher stelle im array der move den namen hat und setze den index auf diese stelle
        for i in range(len(self.movelist)):
            if self.movelist[i][0].name == next_move:
                self.next_move_index = i
                break     
        self.next_move=self.movelist[self.next_move_index]
    
class SpikeSlimeS(MonsterCharacter):
    def __init__(self, id, seed,out_print):
        random.seed(seed)
        hp = random.randint(11, 15)
        super().__init__(monster_id=id, name="Spike Slime (S)", max_hp=hp,out_print=out_print)
        self.movelist = [
            [AttackMove(name="Tackle", damage=6)]
        ]

    def get_next_move(self):
        """
        Determines the next move for the Spike Slime (S).
        """
        self.next_move_index = 0   
        self.next_move=self.movelist[self.next_move_index]