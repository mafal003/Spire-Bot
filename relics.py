class Relic:
    def __init__(self, name, rarity, effect,number=0,used=False):
        self.name = name
        self.rarity = rarity
        # Effect ist eine Funktion, die aufgerufen wird, wenn das Relikt aktiviert wird
        self.effect = effect
        
        self.number = number
        self.used = used

    def __str__(self):
        return self.name + (f" ({self.number})" if self.number is not None else "")
    
    def get_State(self):
        state = {
            "name": self.name,
            "rarity": self.rarity,
            "number": self.number,
            "used": self.used
        }
        maschinereadablestate = [
            # name der zahl wir über relic_names[relicname] aufgelöst und in einem 200 dimensionalen Vektor hot encoded
            relic_name_to_one_hot.get(self.name, [0] * 200),
            relic_rarity_to_one_hot.get(self.rarity, [0] * 10),
            self.number,
            self.used,
        ]
        return state, maschinereadablestate




all_relics = {
    "Burning Blood": Relic("Burning Blood", "Starter", lambda player: player.events.get("on_combat_end").append(
        lambda: (player.heal(6), print(f"Burning Blood healed 6 Player HP {player.current_hp}/{player.max_hp}")))),
}


relic_names = list(all_relics.keys())
# Erstellen von One-Hot-Encodings für Relics dabei bis 200 um raum für misskalkulationen zu lassen
relic_name_to_one_hot = {name: [1 if i == idx else 0 for i in range(200)] for idx, name in enumerate(relic_names)}
rarity = {"Starter":0,"Common":1,"Uncommon":2,"Rare":3,"Special":4,"Boss":5,"Shop":6}
# Erstellen von One-Hot-Encodings für Rarity dabei bis 10 um raum für misskalkulationen zu lassen
relic_rarity_to_one_hot = {name: [1 if i == idx else 0 for i in range(10)] for idx, name in enumerate(rarity.keys())}


# burning blood relic erstellen und state ausgeben

'''
burning_blood = all_relics["Burning Blood"]
print(burning_blood.get_State())

'''