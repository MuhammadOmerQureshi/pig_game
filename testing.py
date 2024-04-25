import random
import json

class Dice:
    @staticmethod
    def roll():
        return random.randint(1, 6)

class DiceHand:
    def __init__(self):
        self.turn_score = 0

    def process_roll(self):
        roll = Dice.roll()
        if roll == 1:
            self.turn_score = 0
        else:
            self.turn_score += roll
        return roll

class Player:
    def __init__(self, name, intelligence=None):
        self.original_name = name
        self.name = name
        self.score = 0
        self.dice_hand = DiceHand()
        self.intelligence = intelligence  # None for human players

    def roll_dice(self):
        roll = self.dice_hand.process_roll()
        self.display_roll(roll)
        return roll

    def display_roll(self, roll):
        if roll == 1:
            print(f"{self.name} rolled a 1. 🎲 No points this turn.")
        else:
            print(f"{self.name} rolled a {roll}. 🎲 Turn total: {self.dice_hand.turn_score}")

    def hold(self):
        self.score += self.dice_hand.turn_score
        print(f"{self.name} holds. Total score: {self.score} 📈")
        self.dice_hand.turn_score = 0

    def cheat(self):
        self.score += 20
        print(f"{self.name} uses CHEAT! +20 points! 🚀")

    def reset(self):
        self.score = 0
        self.dice_hand.turn_score = 0

    def decide_hold(self):
        if self.intelligence:
            return self.intelligence.decide_hold(self.dice_hand.turn_score)
        return False

class Intelligence:
    def __init__(self, threshold=20):
        self.threshold = threshold

    def decide_hold(self, turn_score):
        return turn_score >= self.threshold

class HighScore:
    def __init__(self, histogram):
        self.histogram = histogram

    def update_highscore(self, player):
        self.histogram.update_highscore(player)

class Histogram:
    def __init__(self, filename="highscore.json"):
        self.filename = filename
        self.highscores = self.load_highscores()

    def load_highscores(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def update_highscore(self, player):
        name_key = player.original_name
        player_data = self.highscores.get(name_key, {"name": player.name, "best_score": 0, "games_played": 0})
        player_data["best_score"] = max(player_data["best_score"], player.score)
        player_data["games_played"] += 1
        player_data["name"] = player.name
        self.highscores[name_key] = player_data
        self.save_highscores()

    def save_highscores(self):
        with open(self.filename, "w") as file:
            json.dump(self.highscores, file, indent=4)

    def display_highscores(self):
        for record in self.highscores.values():
            print(f"{record['name']} - Best Score: {record['best_score']}, Games Played: {record['games_played']}")

class Game:
    def __init__(self, players):
        self.players = players
        self.high_score = HighScore(Histogram())

    def play_round(self):
        while True:
            for player in self.players:
                result = self.play_turn(player)
                if result == "quit":
                    return "quit"
                if player.score >= 100:
                    return player

    def play_turn(self, player):
        print(f"\n{player.name}'s turn 🎮")
        while True:
            if player.intelligence:
                # Computer player logic
                player.roll_dice()
                if player.decide_hold() or player.dice_hand.turn_score == 0:
                    player.hold()
                    break
            else:
                # Human player logic
                action = self.get_player_action(player)
                if action in ['r', 'h', 'c', 'q']:
                    if action == 'r':
                        if player.roll_dice() == 1:
                            break
                    elif action == 'h':
                        player.hold()
                        break
                    elif action == 'c':
                        player.cheat()
                    elif action == 'q':
                        return "quit"
                    if player.score >= 100:
                        break

    def get_player_action(self, player):
        valid_actions = {'r', 'h', 'c', 'q'}
        while True:
            action = input(f"{player.name}, roll, hold, or cheat? (r/h/c) or quit game (q): ").lower().strip()
            if action in valid_actions:
                return action
            print("Invalid input, please enter 'r', 'h', 'c', or 'q'.")

def setup_game():
    player1_name = input("Enter Player 1's name: ").strip()
    player1 = Player(player1_name)
    game_mode = input("Play against (1) Computer or (2) another Player? ").strip()

    if game_mode == "1":
        threshold = get_int_input("Choose computer intelligence threshold (1-30): ", 20)
        intelligence = Intelligence(threshold)
        player2 = Player("Computer", intelligence=intelligence)
    else:
        player2_name = input("Enter Player 2's name: ").strip()
        player2 = Player(player2_name)

    return [player1, player2]

def get_int_input(prompt, default):
    try:
        return int(input(prompt))
    except ValueError:
        print(f"Invalid input. Setting to default ({default}).")
        return default

def main():
    players = setup_game()
    game = Game(players)
    while True:
        winner = game.play_round()
        if winner == "quit":
            print("Game has been quit.")
            break
        elif winner:
            print(f"🏆 {winner.name} wins with a score of {winner.score}!")
            game.high_score.update_highscore(winner)
            game.high_score.histogram.display_highscores()

        if input("Do you want to play again? (yes/no): ").lower().strip() != 'yes':
            print("Thanks for playing! 🖐️")
            break
        else:
            for player in players:
                player.reset()

if __name__ == "__main__":
    main()
