# HogStrategy
## Functions
- `probability_of_winning_by_rollling_n(score, opponent_score, n)`
  - computes the win probability of rolling `n` times, up to 10
- `best_num_dice_to_roll(score, opponent_score)`
  - goes through all the possible number of rolls(up to 10) and returns num of dice rolls with the highest win probability
- `probability_of_scoring(k, n, s)`
  - returns the exact probability of scoring `k` points with `n`, `s` sided dice
- `probability_of_winning_with_end_turn_scores(score, opponent_score)`
  - calculates the probability of winning if i end my turn with score and opponent has opponent_score
