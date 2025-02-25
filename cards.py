
#Übersetzung der rarity in eine Zahl 
rarity = {"Basic":0,"Common":1,"Uncommon":2,"Rare":3,"Special":4,"Curse":5}
# Erstellen von One-Hot-Encodings für Rarity dabei bis 10 um raum für misskalkulationen zu lassen
card_rarity_to_one_hot = {name: [1 if i == idx else 0 for i in range(10)] for idx, name in enumerate(rarity.keys())}

class card:
    def __init__(self, name, cost,rarity,actions,value=0,exhaust="False",upgradeable=True,innate=False,playable=True):
        self.name = name
        self.cost = cost
        self.exhaust = exhaust
        self.actions = actions
        #es gibt metaprogression cards die für jedes Mal spielen stärker werden. 
        # Für diese muss es ein Value geben. Bei allen anderen ist der Value 0
        self.value = value
        self.raritiy = rarity
        self.upgradeable = upgradeable
        self.innate = innate
        self.playable = playable

    def __str__(self):
        return self.name
    
    def needs_target(self):
        for action in self.actions:
            if action.target == "enemy":
                return True
        return False

    def play(self,player,cur_target):
        # Karte wird gespielt
        if player.energy < self.cost:
            print("Du hast nicht genug Energie!")
            return
        player.energy -= self.cost
        for action in self.actions:
            action(player,cur_target,self)
        if self.exhaust=="exhaust":
            player.exhausted.append(self)
        else:
            player.discard_pile.append(self)
        player.currentcardplaying = None
        print(f"{player.name} spielt {self.name}!")

    def card_name_to_vector(self):
        vektorspace=3
        name=self.name
        #Es gibt insgesamt wohl so 372 Karten in Slay the Spire?
        card_names = ["Nothing","Strike", "Defend", "Bash", "Slimed"]
        # Erstellen von One-Hot-Encodings für Kartenname dabei erstmal  für Nothing, Strike and Defend
        card_name_to_one_hot = {name: [1 if i == idx else 0 for i in range(vektorspace)] for idx, name in enumerate(card_names)}
        return card_name_to_one_hot.get(name, [0] * vektorspace)


    def get_State(self):
        state = {
            "name": self.name,
            "cost": self.cost,
            "rarity": self.raritiy,
            "value": self.value,
        }

        # name der zahl wir über card_names[cardname] aufgelöst und in einem dimensionalen Vektor hot encoded
        maschinereadablestate =    self.card_name_to_vector()
        '''
        self.cost,
        card_rarity_to_one_hot.get(self.raritiy, [0] * 10),
        self.value,
        '''
        return state, maschinereadablestate

class action:
    def __init__(self, name, target, amount):
        self.name = name
        self.target = target
        self.amount = amount

class Blockaction(action):
    def __init__(self, amount, target="self"):
        super().__init__("block", target, amount)
    def __call__(self, player, target,card):
        if self.target == "self":
            player.add_block(self.amount)
        else:
            target.add_block(self.amount)

class Healaction(action):
    def __init__(self, amount, target="self"):
        super().__init__("heal", target, amount)
    def __call__(self, player, target,card):
        if self.target == "self":
            player.heal(self.amount)
        else:
            target.heal(self.amount)

class Damageaction(action):
    def __init__(self, amount, target):
        super().__init__("damage", target, amount)
    def __call__(self, player, target,card):
        target.take_damage(self.amount, player,card)

class Drawaction(action):
    def __init__(self, amount):
        super().__init__("draw", "self", amount)
    def __call__(self, player, target,card):
        player.draw(self.amount)

class Debuffaction(action):
    def __init__(self, debuff, amount, target):
        super().__init__("apply_debuff", target, amount)
        self.debuff = debuff
    def __call__(self, player, target,card):
        target.add_debuff(self.debuff, self.amount)

#empty card as placeholder
class NothingCard(card):
    def __init__(self):
        super().__init__("Nothing",0,"Basic", [])


class Strike(card):
    def __init__(self):
        super().__init__("Strike",1,"Basic", [Damageaction(6, "enemy")])

class Defend(card):
    def __init__(self):
        super().__init__("Defend",1,"Basic", [Blockaction(5)])

# Ironclad Cards

#Bash deal 8 damage and apply 2 vulnerable
class Bash(card):
    def __init__(self):
        super().__init__("Bash",2,"Basic", [Damageaction(8, "enemy"), Debuffaction("Vulnerable", 2, "enemy")])

#Status Cards

#Slimed costed 1 energy and is exhaustable
class Slimed(card):
    def __init__(self):
        super().__init__("Slimed",1, "Common",[],exhaust="exhaust")

#Curse


#erstelle zum testen ein Strike und lasse den State ausgeben
'''
strike = Defend()
print(strike.get_State())
'''