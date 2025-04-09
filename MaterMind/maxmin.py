import itertools
from functools import lru_cache
import sys

# ---- Configurations ----
COLORS = ['red', 'yellow', 'green', 'blue', 'pink', 'brown']
PEGS = 5

@lru_cache(maxsize=None)
def get_feedback(secret, guess):
    """
    Returns the Mastermind feedback (black, white) given secret and guess.
      - black: Count of pegs that are correct in both color and position.
      - white: Count of pegs that are the correct color but in the wrong position.
    Both secret and guess are tuples of strings.
    """
    black = sum(1 for s, g in zip(secret, guess) if s == g)
    white = sum(min(secret.count(c), guess.count(c)) for c in set(guess)) - black
    return (black, white)

def minimax_guess(remaining, all_codes):
    """
    For each possible guess in all_codes, simulate the feedback for every code in remaining.
    Compute the worst-case (largest) partition size.
    
    Then select the guess that minimizes this worst-case value.
    
    Finally, if more than one guess achieves that minimal score, prefer one that is in `remaining`.
    """
    best_score = float('inf')
    best_guess = None
    
    # First pass: find the lowest worst-case partition size among all codes.
    for guess in all_codes:
        partition_sizes = {}
        for possible_secret in remaining:
            fb = get_feedback(possible_secret, guess)
            partition_sizes[fb] = partition_sizes.get(fb, 0) + 1
        worst_partition = max(partition_sizes.values())
        if worst_partition < best_score:
            best_score = worst_partition
            best_guess = guess
    
    # Second pass: try to find a guess with the same best_score that is also in remaining.
    for guess in all_codes:
        partition_sizes = {}
        for possible_secret in remaining:
            fb = get_feedback(possible_secret, guess)
            partition_sizes[fb] = partition_sizes.get(fb, 0) + 1
        worst_partition = max(partition_sizes.values())
        if worst_partition == best_score and guess in remaining:
            best_guess = guess
            break

    return best_guess

def mastermind_minimax_solver(secret, pegs=PEGS, colors_list=COLORS):
    """
    Solves Mastermind using a minimax approach.
    
    The solver:
      1. Generates all possible codes.
      2. Uses a fixed initial guess for the first move.
      3. Then, at each turn, it chooses the next guess via the minimax criterion (with tie‐breaking preferring candidates from the remaining possibilities).
      4. After each guess, it displays the guess along with its feedback (black and white counts) and
         filters the remaining candidate codes.
    
    Returns the list of guess tuples.
    """
    all_codes = list(itertools.product(colors_list, repeat=pegs))
    remaining = all_codes.copy()  # possible secret codes still valid
    guess_history = []

    # Use a fixed initial guess.
    initial_guess = ('red', 'red', 'yellow', 'green', 'blue')
    guess = initial_guess if initial_guess in all_codes else all_codes[0]
    
    turn = 0
    while remaining:
        turn += 1
        
        # For turn 1 use the fixed initial guess; afterwards use minimax (preferring a valid candidate).
        if turn == 1:
            guess = initial_guess
        else:
            guess = minimax_guess(remaining, all_codes)
        
        guess_history.append(guess)
        feedback = get_feedback(secret, guess)
        
        print(f"\nTurn {turn}: Guessed -> {list(guess)}")
        print(f"   ⚫ Siyah (Black): {feedback[0]}")
        print(f"   ⚪ Beyaz (White): {feedback[1]}")
        
        # Check if the guess is correct.
        if feedback == (pegs, 0):
            print(f"\n✅ Secret code found in {turn} turns!")
            break
        
        # Filter remaining possibilities: only those codes that would produce the same feedback for this guess.
        new_remaining = [code for code in remaining if get_feedback(code, guess) == feedback]
        if len(new_remaining) == len(remaining):
            # No progress made in filtering; we force removal of the guess from remaining.
            if guess in remaining:
                remaining.remove(guess)
            print("➖ No progress from filtering; forcing removal of the guess.")
        else:
            remaining = new_remaining

        # Safety check: if no candidates remain, terminate.
        if not remaining:
            print("❌ No candidates remain. Terminating search.")
            break
    
    return guess_history

if __name__ == "__main__":
    try:
        user_input = input(f"Lütfen renkleri boşluk ile ayırarak giriniz (örnek: red red yellow green blue): ").strip()
        user_sequence = user_input.split()
        invalid_colors = [color for color in user_sequence if color not in COLORS]
        if invalid_colors:
            raise ValueError(f"❌ Hatalı renkler bulundu: {', '.join(invalid_colors)}")
        if len(user_sequence) != PEGS:
            raise IOError(f"Toplam renk sayısı {PEGS} olmalıdır, girilen sayı: {len(user_sequence)}")
        print("✅ Kullanıcının girdiği tüm renkler geçerli!")
    except (ValueError, IOError) as e:
        print(e)
        sys.exit(0)
    
    secret_code = tuple(user_sequence)
    guesses = mastermind_minimax_solver(secret_code, PEGS, COLORS)
    
    print("\nMinimax Strategy Guess Sequence:")
    for i, g in enumerate(guesses, 1):
        print(f"Turn {i}: {list(g)}")

