import math

class Character:
    def __init__(self, character_id, name, max_hp, out_print):
        self.id = character_id
        self.name = name
        self.max_hp = max_hp
        self.block = 0
        self.out_print = out_print
        self.current_hp = max_hp
        self.buffs = {}
        self.buffs_to_add_later = {}
        self.debuffs = {}
        self.clear_events()


    def clear_events(self):
        self.events = {
            "on_take_damage": [],
            "on_turn_start": [],
            "on_turn_end": [],
            "on_unblocked_damage": [],
            "on_combat_end": []
        }


    def take_damage(self, amount,attacker,move=None):
        """
        Verursacht Angriffsschaden beim Charakter. HP können nicht unter 0 fallen. 
        
        :param amount: Die Höhe des Schadens.
                move: Der Move, der den Schaden verursacht hat.
        """
        self.trigger_event("on_take_damage", amount, attacker, move)
        amount = self.calculate_damage(amount, attacker)
        unblocked_damage = amount
        if self.block > 0:
            unblocked_damage = max(0, amount - self.block)
            self.block = max(0, self.block - amount)
        self.current_hp = max(0, self.current_hp - unblocked_damage)
        if self.out_print:
            print(f"{self.name} ({self.id}) nimmt {unblocked_damage} Schaden! HP: {self.current_hp}/{self.max_hp}")

        if unblocked_damage > 0:
            self.trigger_event("on_unblocked_damage", unblocked_damage, attacker, move)
         
    def calculate_damage(self, amount, attacker):
        """
        Berechnet den Schaden, den der Charakter erhält. 
        Falls debuff Vulnerable aktiv ist, wird der erlittene Schaden um 50% erhöht.
        Falls debuff Weak aktiv ist, wird der ausgeteilte Schaden um 25% reduziert.
        
        :param amount: Die Höhe des Schadens.
        :param attacker: Der Angreifer.
        """
        
        attacker_strength = attacker.buffs.get("Strength", 0)
        amount = amount + attacker_strength
        #print(f"Charcter {attacker.name} has Strength: {attacker_strength}")
        if "Vulnerable" in self.debuffs:
            amount = amount * 1.5
        if attacker and "Weak" in attacker.debuffs:
            amount = amount * 0.75

        amount = math.floor(amount)
        return amount

    def heal(self, amount):
        """
        Heilt den Charakter. HP können nicht über das Maximum hinausgehen.
        
        :param amount: Die Höhe der Heilung.
        """
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        if self.out_print:
            print(f"{self.name} ({self.id}) heilt sich um {amount} HP! HP: {self.current_hp}/{self.max_hp}")

    def add_block(self, amount):
        """
        Fügt dem Charakter Block hinzu.
        
        :param amount: Die Höhe des Blocks.
        """
        self.block += amount
        if self.out_print:
            print(f"{self.name} ({self.id}) erhält {amount} Block! Block: {self.block}")

    def add_buff(self, buff_name, buff_value):
        if buff_name in self.buffs:
            self.buffs[buff_name] += buff_value
        else:
            self.buffs[buff_name] = buff_value
        if self.out_print:
            print(f"{self.name} ({self.id}) erhält den Buff: {buff_name} {buff_value}")
        
        if buff_name == "Ritual":
            def apply_ritual_strength(amount, attacker, move):
                if "Ritual" in self.buffs:
                    if not hasattr(self, 'ritual_triggered'):
                        self.ritual_triggered = False  # Initialisiere die Variable beim ersten Aufruf
                    if self.ritual_triggered:
                        self.add_buff("Strength", self.buffs["Ritual"])
                        if self.out_print:
                            print(f"{self.name} ({self.id}) erhält {self.buffs['Ritual']} Stärke durch Ritual!")
                    else:
                        self.ritual_triggered = True  # Setze die Variable auf True beim ersten Mal
                        
            #schaue ob es schon einen callback gibt sonst füge ihn hinzu
            if apply_ritual_strength not in self.events["on_turn_end"]:
                self.register_event("on_turn_end", apply_ritual_strength)

        if buff_name == "Curl Up":
            def apply_curl_up( unblocked_damage, attacker, move):
                if "Curl Up" in self.buffs:
                    self.block += self.buffs["Curl Up"]
                    if self.out_print:
                        print(f"{self.name} ({self.id}) erhält {self.buffs['Curl Up']} Block durch Curl Up!")
                    self.remove_buff("Curl Up")

            self.register_event("on_unblocked_damage", apply_curl_up)

    def remove_buff(self, buff_name):
        if buff_name in self.buffs:
            del self.buffs[buff_name]
            if self.out_print:
                print(f"{self.name} ({self.id}) verliert den Buff: {buff_name}")
        else:
            if self.out_print:
                print(f"{self.name} ({self.id}) hat den Buff {buff_name} nicht.")

    def add_debuff(self, debuff_name, debuff_value):
        if debuff_name in self.debuffs:
            self.debuffs[debuff_name] += debuff_value
        else:
            self.debuffs[debuff_name] = debuff_value
        if self.out_print:
            print(f"{self.name} ({self.id}) erhält den Debuff: {debuff_name} {debuff_value}")

    def remove_debuff(self, debuff_name):
        if debuff_name in self.debuffs:
            del self.debuffs[debuff_name]
            if self.out_print:
                print(f"{self.name} ({self.id}) verliert den Debuff: {debuff_name}")
        else:
            if self.out_print:
                print(f"{self.name} ({self.id}) hat den Debuff {debuff_name} nicht.")

    def register_event(self, event_name, callback):
        if event_name in self.events:
            self.events[event_name].append(callback)
        else:
            self.events[event_name] = [callback]

    def trigger_event(self, event_name, *args):
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(*args)