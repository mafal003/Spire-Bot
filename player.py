from character import Character
from relics import *
import math
import random
from cards import *

class PlayerCharacter(Character):
    def __init__(self, player_id, name, max_hp,out_print):
        super().__init__(player_id, name, max_hp,out_print)
        self.current_potions = []
        self.current_hp = math.floor(max_hp*0.9)
        self.max_potion_number = 2
        self.relics = []
        self.deck = []
        self.hand = []
        self.draw_pile = []
        self.discard_pile = []
        self.exhausted = []
        self.max_energy = 3
        self.energy = self.max_energy
        #speichert falls grade eine Karte gespielt wird, damit sie nicht in der Hand bleibt 
        # und man beim targeten weiß um welche Karte es sich handelt
        self.currentcardplaying = None

    def begin_combat(self):
        self.draw_pile = self.deck.copy()
        self.shuffle_draw_pile()

    def end_combat(self):
        self.hand = []
        self.draw_pile = []
        self.discard_pile = []
        self.exhausted = []
        

    def print_hand(self):
        # soll in einer Zeile ausgegeben werden
        print("Hand:", ", ".join(f"{i}: {card}" for i, card in enumerate(self.hand)))

    def print_draw_pile(self):
        # soll in einer Zeile ausgegeben werden
        print("Draw Pile:", ", ".join(f"{i}: {card}" for i, card in enumerate(self.draw_pile)))

    def print_discard_pile(self):
        # soll in einer Zeile ausgegeben werden
        print("Discard Pile:", ", ".join(f"{i}: {card}" for i, card in enumerate(self.discard_pile)))

    def draw(self, amount):
        '''
        Zieht eine bestimmte Anzahl an Karten. 
        Wenn der draw pile leer ist, wird der discard pile gemischt und zum draw pile. 
        '''
        for i in range(amount):
            if len(self.draw_pile) == 0:
                self.reshuffle_discard_pile()
            if len(self.draw_pile) == 0:
                # Wenn der discard pile auch leer ist, kann nicht weiter gezogen werden.
                if self.out_print:
                    print("Du hast keine Karten mehr im Deck!")
                break
            card = self.draw_pile.pop()
            self.hand.append(card)
            if self.out_print:
                print(f"Du ziehst {card}.")

    def discard_hand(self):
        '''
        Discardet alle Karten in der Hand.
        '''
        self.discard_pile += self.hand
        self.hand = []
        if self.out_print:
            print("Deine Hand wurde verworfen.")

    def shuffle_draw_pile(self):
        random.shuffle(self.draw_pile)
        
    def reshuffle_discard_pile(self):
        '''
        Mische den discard pile und füge ihn zum draw pile hinzu.
        '''
        self.draw_pile += self.discard_pile
        self.shuffle_draw_pile()
        self.discard_pile = []

    def add_potion(self, potion):
        if len(self.current_potions) < self.max_potion_number:
            self.current_potions.append(potion)
        else:
            if self.out_print:
                print("Du kannst keine weiteren Tränke aufnehmen!")

    def use_potion(self, potion_index):
        if 0 <= potion_index < len(self.current_potions):
            potion = self.current_potions.pop(potion_index)
            if self.out_print:
                print(f"Du benutzt {potion}.")
        else:
            if self.out_print:
                print("Ungültiger Trankindex!")

    def add_relic(self, relic):
        self.relics.append(relic)
        if self.out_print:
            print(f"Du hast ein neues Relikt erhalten: {relic}")

    def add_temp_card(self,cardname,position,statusnumber):
        #temporäre Karten werden erstmal entfernt um das Spiel zu vereinfachen
        '''

        #ein meiner meinung nach sehr ugly hack, um die Karten zu erstellen AKA Class muss gleich cardname sein damit es funktioniert
        card = globals()[cardname]()
        if (position == "Draw Pile"):
            for i in range(statusnumber):
                self.draw_pile.append(card)
            self.draw_pile.append(card)
        if (position == "Discard Pile"):
            for i in range(statusnumber):
                self.discard_pile.append(card)
        print(f"Du hast folgende Karte erhalten: {card}")
        '''


    def add_cards(self, cards):
        self.cards.extend(cards)
        if self.out_print:
            print(f"Du hast folgende Karten erhalten: {cards}")


    def get_State(self):
        state = {
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "current_potions": self.current_potions,
            "max_potion_number": self.max_potion_number,
            #aufrufen der get_State bei den Relics
            "relics": [relic.get_State()[0] for relic in self.relics],
            #aufrufen der get_State bei den Karten
            "deck": [card.get_State()[0] for card in self.deck],
            "hand": [card.get_State()[0] for card in self.hand],
            "draw_pile": [card.get_State()[0] for card in self.draw_pile],
            "discard_pile": [card.get_State()[0] for card in self.discard_pile],
            "exhausted": [card.get_State()[0] for card in self.exhausted],
            "max_energy": self.max_energy,
            "energy": self.energy
        }

        def pad_cards(cards, max_length=5):

            anzahlKarten = len(cards)
            padded_cards =[]
            for card in cards:
                cardstate=card.get_State()[1]
                padded_cards+=cardstate
            leereKarte=globals()["NothingCard"]()
            while anzahlKarten < max_length:
                padded_cards+=leereKarte.get_State()[1]  # leere Karte hinzufügen
                anzahlKarten += 1
            return padded_cards
        
        
        if self.currentcardplaying is None:
            current_card_state = globals()["NothingCard"]().get_State()[1]
        else:
            current_card_state = self.currentcardplaying.get_State()[1]

        maschinereadablestate = [
            self.current_hp,
            self.energy
        ] + pad_cards(self.hand) + current_card_state



        '''
        [card.get_State()[1] for card in self.draw_pile],
        [card.get_State()[1] for card in self.discard_pile],
        [card.get_State()[1] for card in self.exhausted],
        '''
        return state, maschinereadablestate


        

class Ironclad(PlayerCharacter):
    def __init__(self,out_print):
        super().__init__("0", "Ironclad", 75,out_print)
        self.add_relic(all_relics["Burning Blood"])
        self.deck = [Strike() for _ in range(5)] + [Defend() for _ in range(5)]