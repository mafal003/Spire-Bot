#In dieser File teste ich die Funktionalität des Spiels
from world import *


# Generiere einen zufälligen Seed
seed = random.randint(0, 1000000)
seed = 111857
#seed=193080
# Beispiel für die Erstellung einer Welt
welt = World(seed=seed)
welt = World(seed=seed,autoplay=True)


# Testen des Cultist-Monsters
#cultist = Cultist("Monster001", 123452)

# Testen des Red Louse-Monsters
#red_louse = RedLouse("Monster002", 123425)

#JawWorm = JawWorm("Monster003", 123425)

#AcidSlimeM = AcidSlimeM("Monster004", 123425)
#AcidSlimeS = AcidSlimeS("Monster005", 123425)

i=0
'''
TODO States ausgeben können
TODO States Laden können
TODO Karten erstellen
'''

# Solange der Spieler am Leben ist, die Welt versucht nach dem Encounter den nächsten Floor zu betreten

print("anfang12")
while welt.situation != "Game Over":
    #gamestate holen
    gamestate = welt.get_state_human()
    #print(gamestate)
    #actionspace holen
    actionspace = welt.get_action_space()
    print("ActionSpace:",actionspace)
    #action auswählen
    action = ""
    if (welt.autoplay):
        #bei autoplay wird immmer letze action des actionspace genommen,
        #da es somit solange es eine karte gibt eine karte gespielt wird anstatt zu passen

        action = actionspace[-1]

    else:
        #wähle durch input action aus dem actionspace aus
        while action not in actionspace:
            action = input("Enter action: ")
            try:
                action = actionspace[int(action)-1]
            except:
                print("Invalid action")
    # gib die karte aus die gespielt wird
    if (action.startswith("Play card")):
        print("Karte die gespielt wird:",welt.player.hand[int(action.split(":")[1])-1].name)
    print("Taking action: ", action)
    #action ausführen
    welt.take_action(action)