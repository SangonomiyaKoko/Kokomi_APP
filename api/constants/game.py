class GameData:
    SHIP_TYPES = {
        'AirCarrier','Battleship','Cruiser','Destroyer','Submarine'
    }

    SHIP_TIERS = set(range(1, 12))

    SHIP_NATIONS = {
        'commonwealth','europe','france','germany','italy',
        'japna','netherlands','pan_america','pan_asia',
        'spain','uk','usa','ussr'
    }