import os
import random
from difflib import SequenceMatcher
from abc import ABC, abstractmethod


class GameLogic(ABC):

    def __init__(self, num_words, length, attempts):
        """Set up a new game with the provided parameters"""
        self.num_words = num_words
        self.length = length
        self.attempts = attempts
        self.words = self.word_selection()
        self.password = random.choice(self.words)

    @abstractmethod
    def word_selection(self):
        pass

    @abstractmethod
    def check(self, guess):
        pass


class NumberLogic(GameLogic):

    def word_selection(self):
        words = []
        digits = "0123456789"

        while len(words) < self.num_words:
            num = ""
            while len(num) < self.length:
                e = random.choice(digits)
                num += e
            if num not in words:
                words.append(num)

        return words

    def check(self, guess):
        """Check a guess and give feedback"""
        if len(guess) != self.length:
            return False, ["Wrong length"]
        if guess == self.password:
            return True, ["Access granted!"]
        else:
            matching = 0
            for num in guess:
                for pw_num in self.password:
                    if num == pw_num:
                        matching += 1
            self.attempts = self.attempts - 1
            return False, ["%d/%d correct" % (matching, self.length), "Access denied!"]


class WordLogic(GameLogic):
    """Internal game logic"""

    def compute_similarity(self, a, b, threshold):
        s = SequenceMatcher(None, a, b)
        if s.ratio() > threshold:
            return True
        return False

    def word_selection(self):
        words = []
        one_third = self.num_words // 3
        two_thirds = self.num_words - one_third

        with open("words.txt") as f:
            word_list = f.read().splitlines()

        fixed_length_words = [word.upper() for word in word_list if len(word) is self.length]

        # Pick one third of the words at random
        for x in range(one_third):
            e = random.choice(fixed_length_words)
            words.append(e)
            fixed_length_words.remove(e)    # remove to avoid having duplicates

        # For the remaining two thirds:
        for x in range(two_thirds):
            a = random.choice(words)                # (a) pick at random any word already selected
            b = random.choice(fixed_length_words)   # (b) pick at random a word from the word pool
            # check if it is more than 60% similar to the random pick in (a)
            while not self.compute_similarity(a, b, 0.6):
                b = random.choice(fixed_length_words)
            words.append(b)
            fixed_length_words.remove(b)

        random.shuffle(words)
        return words

    def check(self, guess):
        """Check a guess and give feedback"""
        if len(guess) != self.length:
            return False, ["Wrong length"]
        if guess == self.password:
            return True, ["Access granted!"]
        else:
            matching = 0
            for i in range(self.length):
                if guess[i] == self.password[i]: matching += 1
            self.attempts = self.attempts - 1
            return False, ["%d/%d correct" % (matching, self.length), "Access denied!"]


class GameRunner(object):
    """Interactive game front-end"""

    def __init__(self, logic):
        """Interact with the given game logic"""
        self.logic = logic
        self.rows = 17
        self.columns = 2
        self.colwidth = 12
        self.code_snippet = self.generate_code_lines()
        self.hex_codes = self.generate_hex_codes()

    def generate_hex_codes(self):
        chars = "0123456789ABCDEF"
        hexes = []
        nr_hexes = self.columns * self.rows

        for j in range(nr_hexes):
            hex_code = "0x"
            for i in range(4):
                rand_char = random.choice(chars)
                hex_code += rand_char
            hexes.append(hex_code)

        return hexes

    def generate_code_lines(self):
        padding_chars = "<>[]{}()'|\"!@#$%^&*-_+=.;:?,/"
        len_snippet = self.rows * self.columns * self.colwidth
        len_words = self.logic.num_words * self.logic.length
        len_paddings = len_snippet - len_words
        padding_size = int(len_paddings / (self.logic.num_words + 1))

        def generate_padding():
            return "".join([random.choice(padding_chars) for i in range(padding_size)])

        text = ""
        text += generate_padding()
        for word in self.logic.words:
            text += "".join([c for c in word])
            text += generate_padding()
        text += generate_padding()
        text = text[:len_snippet]
        return [text[i:i + self.colwidth] for i in range(0, len(text), self.colwidth)]

    def print_screen(self, history):
        """Redraw the entire terminal screen with the given content"""
        # Clear the terminal screen
        print()
        os.system('cls' if os.name == 'nt' else 'clear')
        # Print screen contents
        print("ROBCO INDUSTRIES (TM) TERMALINK PROTOCOL\n" + \
              "ENTER PASSWORD NOW\n\n" + \
              str(self.logic.attempts) + " ATTEMPT(S) LEFT:" + (" █" * self.logic.attempts) + "\n")
        local_history = history[-self.rows + 1:]
        history_lines = ["" for i in range(self.rows - len(local_history) - 1)] + \
                        [">%s" % l for l in local_history] + [">"]
        for row in range(self.rows):
            # print address and text cells
            for column in range(self.columns):
                offset = self.rows * column
                index = offset + row
                print("%s %s  " % (self.hex_codes[index], self.code_snippet[index]), end="")
            print(history_lines[row], end="")
            if not row == self.rows - 1:
                print()

    def run(self):
        """Run the game main loop"""

        history = []

        self.print_screen(history)
        while self.logic.attempts != 0:
            guess = input().upper()
            history.append(guess)
            access, feedback = logic.check(guess)
            history.extend(feedback)
            self.print_screen(history)
            if access:
                break


if __name__ == '__main__':
    logic = WordLogic(num_words=7, length=4, attempts=4)
    runner = GameRunner(logic)
    runner.run()

