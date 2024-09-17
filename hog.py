"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact
import sys
from typing import Callable, Union

MAX_RECURSION_DEPTH = 10000
MAX_DICE_ROLLS = 10
GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'

    rolled_one = False
    sum = 0
    i = 0
    # rolls the dice num_rolls times, storing the sum in roll_res
    # if a 1 is rolled, flip rolled_one to True
    while i < num_rolls:
        roll_res = dice()
        if roll_res == 1:
            rolled_one = True
        sum += roll_res
        i += 1

    # return sum of dice rolls if 1 isn't rolled, returns 1 otherwise
    return 1 if rolled_one else sum

def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    # Free Bacon if choose to roll 0
    if num_rolls == 0:
        return max(opponent_score % 10, opponent_score // 10) + 1
    else:
    # Result of rolling dice num_rolls times
        return roll_dice(num_rolls, dice)

# Playing a game

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).

    >>> select_dice(4, 24) == four_sided
    True
    >>> select_dice(16, 64) == six_sided
    True
    >>> select_dice(0, 0) == four_sided
    True
    """
    if (score + opponent_score) % 7 == 0:
        return four_sided
    else:
        return six_sided

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """
    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score, opponent_score = 0, 0
    # the game plays until a player reaches 100 points
    while score < goal and opponent_score < goal:
        # hog wild rule
        dice = select_dice(score, opponent_score)
        # take turn with player 0 if current turn belongs to player 0
        # otherwise take turn with player 1 if current turn belongs to player 1
        if who == 0:
            score += take_turn(strategy0(score, opponent_score), opponent_score, dice)
        else:
            opponent_score += take_turn(strategy1(opponent_score, score), score, dice)
        # swine swap rule 
        if score * 2 == opponent_score or opponent_score * 2 == score:
            score, opponent_score = opponent_score, score
        # switch to other player after current player's turn ends
        who = other(who)

    return score, opponent_score

#######################
# Phase 2: Strategies #
#######################

# Basic Strategy

BASELINE_NUM_ROLLS = 5
BACON_MARGIN = 8

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def avg_value(*args):
        i = 0
        res = 0
        while i < num_samples:
            res += fn(*args)
            i += 1
        return res / num_samples

    return avg_value

def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    highest_avg = 0
    highest_roll = 1

    i = 1
    while i <= 10:
        current_avg = make_averaged(roll_dice)(i, dice)
        print(str(i) + ' dice scores ' + str(current_avg) + ' on average')
        if current_avg > highest_avg:
            highest_avg = current_avg
            highest_roll = i
        i += 1

    return highest_roll

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(BASELINE_NUM_ROLLS)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Changed to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score):
    """This strategy rolls 0 dice if that gives at least BACON_MARGIN points,
    and rolls BASELINE_NUM_ROLLS otherwise.

    >>> bacon_strategy(0, 0)
    5
    >>> bacon_strategy(70, 50)
    5
    >>> bacon_strategy(50, 70)
    0
    """
    # If free bacon rule would give at least BACAON_MARGIN POINTS
    if max(opponent_score % 10, opponent_score // 10) + 1 >= BACON_MARGIN:
        return 0
    else:
        return BASELINE_NUM_ROLLS


def swap_strategy(score, opponent_score):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls BASELINE_NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least BACON_MARGIN points and rolls
    BASELINE_NUM_ROLLS otherwise.

    >>> swap_strategy(23, 60) # 23 + (1 + max(6, 0)) = 30: Beneficial swap
    0
    >>> swap_strategy(27, 18) # 27 + (1 + max(1, 8)) = 36: Harmful swap
    5
    >>> swap_strategy(50, 80) # (1 + max(8, 0)) = 9: Lots of free bacon
    0
    >>> swap_strategy(12, 12) # Baseline
    5
    """
    free_bacon_score = score + max(opponent_score % 10, opponent_score // 10) + 1

    if free_bacon_score * 2 == opponent_score:
        return 0
    elif free_bacon_score == opponent_score * 2:
        return BASELINE_NUM_ROLLS
    else:
        return bacon_strategy(score, opponent_score) 

##########################
# Final Strategy #
##########################
# Algorithm inspired by the following blog post:
# Source: https://old.paulbramsen.com/archives/32
def final_strategy(score, opponent_score):
    """This strategy uses a recursive approach to calculate the optimal number of dice to roll based on:
    - The current score and opponent_score
    - Probability of winning for each possible number of dice to roll

    The optimal number of dice is determined by comparing the probability of winning for each potential option, and choosing the highest 
    """
    return best_num_dice_to_roll(score, opponent_score)

def memoized(func) -> Callable[..., Union[int, float]]:
    """Decorator that caches previously seen results and returns the memoized ver of func

    @param: func: a function that computes some result
    @return: func: memoized version of func    
    """
    cache = {}

    def wrapper(*args):
        # if already seen, return the result
        if args in cache:
            return cache[args]
        # stores the result of func(args) in the cache and returns the value
        result = func(*args)
        cache[args] = result
        return result

    return wrapper

@memoized
def best_num_dice_to_roll(score, opponent_score) -> int:
    """Returns the best number of dice to roll on my turn based on score and opponent score
    
    @param score: my score
    @param opponent_score: opponent's score

    @return: best number of dice to roll
    """
    # Sets recursion limit to MAX_RECURSION_DEPTH
    if sys.getrecursionlimit() < MAX_RECURSION_DEPTH:
        sys.setrecursionlimit(MAX_RECURSION_DEPTH)

    best_probability, best_num_of_dice = 0, 1

    num_of_dice = 0
    while num_of_dice <= MAX_DICE_ROLLS:
        # Iterate through number of possible dice rolls, finding best probability of winning
        curr_probability = probability_of_winning_by_rolling_n(score, opponent_score, num_of_dice)
        if curr_probability > best_probability:
            best_probability = curr_probability
            best_num_of_dice = num_of_dice

        num_of_dice += 1

    return best_num_of_dice

@memoized
def probability_of_winning_by_rolling_n(score, opponent_score, n) -> float:
    """Computes the win probability of rolling the dice n times 

    @param: score: my score
    @param: opponent_score: opponent's score
    @param: n: the number of dice rolls, 0 <= n <= 10

    @return: the probability of winning 
    """
    free_bacon_score = max(opponent_score % 10, opponent_score // 10) + 1
    sides = 6
    # Hog wild 
    if (score + opponent_score) % 7 == 0:
        sides = 4
    win_probability = 0
    
    if n == 0:
        # Free bacon
        turn_score = free_bacon_score
        win_probability = probability_of_winning_with_turn_end_scores(score + turn_score, opponent_score)
    else:
        # Iterate over all possible scores to calculate the probability of winning
        possible_score = 1
        while possible_score <= sides * n:
            win_probability += (probability_of_scoring(possible_score, n, sides)) * probability_of_winning_with_turn_end_scores(score + possible_score, opponent_score)
            possible_score += 1

    return win_probability

@memoized
def probability_of_winning_with_turn_end_scores(score, opponent_score) -> float:
    """Calculates the probability of winning if I end my turn with score and opponent has opponent_score
    
    @param score: int: my score
    @param opponent_score: opponent's score

    @return: the probability of winning when I end my turn with score and opponent has opponent_score

    """
    # Swine swap
    if score * 2 == opponent_score or opponent_score * 2 == score:
        score, opponent_score = opponent_score, score
    if score >= GOAL_SCORE:
        return 1
    elif opponent_score >= GOAL_SCORE:
        return 0
    # Assume opponent's strategy is optimal
    opponent_num_rolls = best_num_dice_to_roll(opponent_score, score)
    probability_of_opponent_winning = probability_of_winning_by_rolling_n(opponent_score, score, opponent_num_rolls)

    return 1 - probability_of_opponent_winning

# The following functions are derived from Professor John DeNero's fa13 Lecture 8 Video 5 on winning Hog
# Source: https://youtu.be/xqRosBPbUXI?si=F5O5MSTI_nyr3sfK  
@memoized    
def number_of_ways_to_score(k, n, s) -> int:
    """Calculates the number of ways that k can be scored by rolling n
    s-sided dice without incurring the Pig Out Rule

    @param k: int: the points to score
    @param n: int: the number of dice rolls 0 <= 0 <= 10
    @param s: int: the sides of dice 4 or 6

    @return: number of ways to score k with n s-sided dice

    """
    if n == 0:
        if k == 0:
            return 1
        return 0

    ways, dice = 0, 2
    while dice <= s:
        ways += number_of_ways_to_score(k - dice, n - 1, s)
        dice += 1

    return ways

@memoized
def probability_of_scoring(k, n, s) -> float:
    """Calculates probability of scoring k points with n s-sided dice
    
    @param k: int: the points to score
    @param n: int: the number of dice rolls 0 <= 0 <= 10
    @param s: int: the sides of dice 4 or 6

    @return: probability of scoring k points with n s-sided dice

    """
    if k == 1:
        return 1 - pow(s - 1, n) / pow(s, n)
    return number_of_ways_to_score(k, n, s) / pow(s, n)

##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.

def get_int(prompt, min):
    """Return an integer greater than or equal to MIN, given by the user."""
    choice = input(prompt)
    while not choice.isnumeric() or int(choice) < min:
        print('Please enter an integer greater than or equal to', min)
        choice = input(prompt)
    return int(choice)

def interactive_dice():
    """A dice where the outcomes are provided by the user."""
    return get_int('Result of dice roll: ', 1)

def make_interactive_strategy(player):
    """Return a strategy for which the user provides the number of rolls."""
    prompt = 'Number of rolls for Player {0}: '.format(player)
    def interactive_strategy(score, opp_score):
        if player == 1:
            score, opp_score = opp_score, score
        print(score, 'vs.', opp_score)
        choice = get_int(prompt, 0)
        return choice
    return interactive_strategy

def roll_dice_interactive():
    """Interactively call roll_dice."""
    num_rolls = get_int('Number of rolls: ', 1)
    turn_total = roll_dice(num_rolls, interactive_dice)
    print('Turn total:', turn_total)

def take_turn_interactive():
    """Interactively call take_turn."""
    num_rolls = get_int('Number of rolls: ', 0)
    opp_score = get_int('Opponent score: ', 0)
    turn_total = take_turn(num_rolls, opp_score, interactive_dice)
    print('Turn total:', turn_total)

def play_interactive():
    """Interactively call play."""
    strategy0 = make_interactive_strategy(0)
    strategy1 = make_interactive_strategy(1)
    score0, score1 = play(strategy0, strategy1)
    print('Final scores:', score0, 'to', score1)

@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--interactive', '-i', type=str,
                        help='Run interactive tests for the specified question')
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.interactive:
        test = args.interactive + '_interactive'
        if test not in globals():
            print('To use the -i option, please choose one of these:')
            print('\troll_dice', '\ttake_turn', '\tplay', sep='\n')
            exit(1)
        try:
            globals()[test]()
        except (KeyboardInterrupt, EOFError):
            print('\nQuitting interactive test')
            exit(0)
    elif args.run_experiments:
        run_experiments()
