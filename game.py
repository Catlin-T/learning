import os
import time
import sys
from random import randint, choice


class Character(object):
    """Should be able to use this class for both
    enemies *and* the human player.

    Example:
        >>> derp = Character.random('goblin', level=5)
        >>> derp = Character('human', attack=44, ...)

    """

    def __init__(self, name, attack=1, defense=1, agility=1,
                 luck=1, hitpoints=10, level=1, experience=0):

        """

        Args:
            name (str): --
            experience (int): If this is the human player,
                this is the total experience gained. However,
                if this is an enemy, this value represents
                the experience gained by killing this enemy.

        """

        self.name = name
        self.attack = attack
        self.defense = defense
        self.agility = agility
        self.luck = luck
        self.hitpoints = hitpoints
        self.level = level
        self.experience = experience

        self.max_hitpoints = hitpoints

        self.stat_labels = {
                            "ATK": "attack",
                            "DEF": "defense",
                            "AGL": "agility",
                            "LCK": "luck"
                           }

    @classmethod
    def from_assigned(cls, name, points_to_assign):
        """Create a character object, by interactively
        promting the user to distribute n points among
        their stats.

        Args:
            name (str): The name of this character, e.g.,
                "Cool Girl the Awesome."
            points_to_assign (int): Number of points to
                interactively distribute into stats.

        Returns:
            Character: Whose stats are created from
                character.assign_points().

        Notes:
            Another good name would be "from_interactive."

        """

        character = cls(name)
        character.assign_points(points_to_assign)

        return character

    @classmethod
    def random(cls, name, level):
        """Create an character instance of "name"
        with randomly generated stats.
        
        Args:
            name (str): The name of this character, e.g.,
                "Goblin."
            level (int): The level of the character that is
                being generated. This affects the number of
                points that get randomly distributed through
                out the character's stats.

        Returns:
            Character: Whose stats are generated randomly.

        """

        # generate some random stats
        # use this class' init function
        # to produce and return a character
        if level < 1:
            level = 1
        
        # Generated characters get the same number of points as player
        points_to_assign = level
        
        # Add additional points per level at the same rate as player
        for num in range(level):
            points_to_assign += level

        # Temporary holder for character stat values
        stats = {
                "attack": 0,
                "defense": 0,
                "agility": 0,
                "luck": 0,
                }

        # Assign each point randomly
        for point in range(points_to_assign):
            stats[choice(stats.keys())] += 1

        # NOTE: some people (me) hate this
        # kind of formatting because it's
        # hard to maintain and oftenly
        # inconsistent in style.
        attack    = stats["attack"]
        defense   = stats["defense"]
        agility   = stats["agility"]
        luck      = stats["luck"]
        hitpoints = randint(1, 10)

        experience = level * randint(11, 16)

        character = cls(name, attack, defense, agility,
                        luck, hitpoints, level, experience)

        return character

    def assign_points(self, points):
        """Namely for HumanPlayer to distribute
        their stats into the hero.

        Args:
            points (int): Number of points to invest
                in stats.

        """

        while points > 0:
            # NOTE:
            # use textwrap.dedent with a ''' string
            # i personally like to use ''' for non-docstring multi
            # line strings
            print "\nYou have %s points remaining" % points
            print "Assign points by typing in the stat you want to boost.\n"
            print "ATK: %s" % self.attack
            print "DEF: %s" % self.defense
            print "AGL: %s" % self.agility
            print "LCK: %s \n" % self.luck
            selection = raw_input("$").upper()
            
            if selection in self.stat_labels:
                # Increase the selected stat by one
                setattr(self, self.stat_labels[selection], 
                        getattr(self, self.stat_labels[selection]) + 1)
                points -= 1

            else:
                print "\nTry Again.\n"

    def next_xp_goal(self):
        """Return the total XP required to reach
        the next level. NOT how much to the next
        level, but the goal XP for the next level.

        Level experience requirements are exponential.

        Level    XP
        1        -
        2        300
        3        450
        4        600
        5        750
        6        900
        7        1050
        8        1200
        9        1350
        10       1500

        And so on, there is no level limit, this is
        an equation.

        Notes:
            base_xp is how much XP to the next level, every
            level prior to the factor (bonus/increase).

        Returns
            int: The next level's XP goal.

        """

        base_xp = 100
        factor = 1.5

        # this is a doozie because of the finitely
        # abelian group/type math in Python 2 vs.
        # Python 3
        return int(base_xp * (self.level + 1 ** factor))

    def level_up(self):
        """Level up if possible, return True if
        leveled up, else False.
        
        Return:
            bool: True if leveled up, False if not.

        """

        if self.experience >= self.next_xp_goal():
            self.assign_points(self.level)
            self.level += 1

            return True

        else:

            return False

    def print_stats(self):
        """Print the current stats of the player 
        to the console.

        """
        
        # attribute name, print name
        order = {
            'hitpoints': 'HP', 
            'attack': 'ATK', 
            'defense': 'DEF', 
            'agility': 'AGL', 
            'luck': 'LCK'
            }

        print "Level %s %s\n" % (self.level, self.name)
        print("%s/%s XP" % (self.experience, self.next_xp_goal()))

        for stat, print_name in order.iteritems():
            print "%s: %s" % (print_name, getattr(self, stat))
    
    def punch(self, defender):
        """Attack the defender!

        This object will deal damage to the defender.

        Attributes Used:
            defender.luck (int): This is halved and then used to
                generate a defense bonus.
            defender.defense (int): This defends against self.attack
            defender.hitpoints (int): Once the damage is calculated,
                this is what it gets subtracted from.
            self.luck (int): Is used to generate an attack bonus
            self.attack (int): Base value used for calculating damage.

        Args:
            defender (Character): The character getting attacked.

        """
        
        d20 = Die(20)

        bonuses = d20.attack_roll(self.luck, defender.luck)
        attacker_bonus, defender_bonus, critical = bonuses
 
        attacker_bonus += self.attack
        defender_bonus += defender.defense

        if critical:
            defender_bonus /= 2

        damage = attacker_bonus - defender_bonus

        if critical and damage < 1:
            damage = 1

        elif damage < 1:
            damage = 0
        
        defender.hitpoints -= damage

        #Print statements

        if critical:
            print "CRITICAL!"

        if damage == 0:
            print "Missed!"

        else:
            print "%s hit %s for %s damage" % (self.name, defender.name, damage)
        


class Die(object):
    """Die object that will be used to calculate and
    execute probabilities.

    Examples:
        >>> d20 = Die(20)
        >>> d6 = Die(6)

    """

    def __init__(self, sides):
        """
        Args:
            sides (int): The number of possible sides.
        
        """

        self.sides = sides

    def roll(self):
        """Rolls the die and returns the number it landed on.

        Returns:
            int: Between 1 and self.sides

        """

        return randint(1, self.sides)

    def attack_roll(self, atk_luck, def_luck):
        """Calculates the attack bonus and if it's a critical hit.

        Args:
            atk_luck (int): The attacker's luck value.
            def_luck (int): The defender's luck value.

        Returns:
            total_results (tup): a tuple containing the following
                results -- (atk_bonus, def_bonus, critical)
            atk_bonus (int): The total attack bonus from the roll.
            def_bonus (int): The total defense bonus from the roll.
            critical (bool): Whether or not it's a critical hit.

        """
        
        critical = False
        critical_threshold = atk_luck - def_luck

        if critical_threshold > 8: #crit chance cannot be greater than 40%
            critical_threshold = 8

        elif critical_threshold < 1: #crit chance cannot be less than 5%
            critical_threshold = 1

        critical_threshold = self.sides - critical_threshold 

        atk_result = self.roll() #roll the die!
        def_result = self.sides - atk_result #if atk rolls low, def high

        if atk_result >= critical_threshold: #did we roll above crit threshold?
            critical = True

        atk_bonus = (atk_result * atk_luck) / self.sides
        def_bonus = (def_result * def_luck) / self.sides

        total_results = (atk_bonus, def_bonus, critical)

        return total_results


def battle(player, baddy):

    agl_check = baddy.agility > player.agility

    if agl_check:
        print "\nOh no! the enemy strikes first!"

    while True:
    
        if agl_check:
            baddy.print_stats()

            print "\nIt's this guy's turn.\n"
            raw_input("Enter to continue.")
            
            baddy.punch(player)
            
            if player.hitpoints <= 0: break
            
            print

            player.print_stats()

            print "\nIt's your turn.\n"
            raw_input("Enter to continue.")

            player.punch(baddy)

            if baddy.hitpoints <= 0: break
            
            print

        else:
            player.print_stats()
            
            print "\nIt's your turn.\n"
            raw_input("Enter to continue.")
            
            player.punch(baddy)
            
            if baddy.hitpoints <= 0: break
            
            print

            baddy.print_stats()

            print "\nIt's this guys turn.\n"
            raw_input("Enter to continue.")

            baddy.punch(player)

            if player.hitpoints <= 0: break
                
            print

    if player.hitpoints <= 0:
        sys.exit("You died.")
    else:
        print "\nYou killed the %s!" % (baddy.name)
        player.experience += baddy.experience
        player.hitpoints = player.max_hitpoints #heal player after fight
        
        player.level_up() #check if player can level up


def main():
    # NOTE: this is a tenary
    os.system('clear' if os.name == 'posix' else 'cls')
    
    name = raw_input("What's your name? ")
    player = Character.from_assigned(name, points_to_assign=4)

    print "\n*BOOM*"

    time.sleep(2)

    print "\n*BOOM BOOM*"

    time.sleep(2)

    print "\nHEY! Get up! We're under attack!"
    print "Get your ass up, pick up a weapon, and defend the village!"

    time.sleep(1)

    print "\n..."

    time.sleep(1)

    print "\nWelp, no weapons."
    print "Looks like our feline god named 'Lin' has forsaken you."
    print "Now go fight.\n"

    while True:
        #min and max level that enemies can be
        max_level = player.level + 1
        min_level = player.level - 2
        enemy_level = randint(min_level, max_level)

        enemy = Character.random('goblin', enemy_level)
        battle(player, enemy)

    return None

if __name__ == "__main__":
    main()
