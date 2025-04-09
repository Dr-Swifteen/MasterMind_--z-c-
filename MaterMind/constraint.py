import itertools
import random
import sys
from functools import lru_cache

# Configuration: allowed colors and code length
COLORS = ['red', 'yellow', 'green', 'blue', 'pink', 'brown']
PEGS = 5

@lru_cache(maxsize=None)
def get_feedback(secret, guess):
    """
    Compute Mastermind feedback.
      - Siyah (black): number of pegs where the guess has the correct color and position.
      - Beyaz (white): number of correct colors in wrong positions.
    Both secret and guess are tuples of strings.
    """
    black = sum(1 for s, g in zip(secret, guess) if s == g)
    white = sum(min(secret.count(c), guess.count(c)) for c in set(guess)) - black
    return (black, white)

def logical_inference_solver(secret, pegs=PEGS, colors_list=COLORS, num_initial_guesses=3):
    """
    Logical Inference Mastermind Solver
    
    The approach:
    1. Random Exploration: Choose a few (num_initial_guesses) random guesses.
       For each, obtain feedback and narrow the candidate set to those that yield
       the same feedback against that guess. The feedback from each guess is
       internally stored as a "premise" (transformed into CNF-like constraints).
    2. Inference Phase: From the remaining candidate codes, choose the guess that
       is most "consistent" with all past feedback. Here we compute, for each candidate,
       a score that sums differences between its predicted feedback for each previous guess
       and the recorded feedback. The candidate with the smallest score is chosen.
    3. Iteratively add the new guess’s feedback as an additional constraint and
       filter the candidate list until the secret is found.
    """
    # Generate all possible codes (the full search space)
    all_codes = list(itertools.product(colors_list, repeat=pegs))
    remaining = all_codes.copy()  # Candidate codes that are still valid
    guess_history = []
    premises = []  # Each element is a tuple: (guess, feedback)
    turn = 0

    # Phase 1: Make a few random initial guesses.
    for _ in range(num_initial_guesses):
        turn += 1
        guess = random.choice(remaining)
        guess_history.append(guess)
        fb = get_feedback(secret, guess)
        print(f"\nTurn {turn}: Guessed -> {list(guess)}")
        print(f"   ⚫ Siyah (Black): {fb[0]}")
        print(f"   ⚪ Beyaz (White): {fb[1]}")
        # Add the (hidden) premise: any valid code must yield this feedback for this guess.
        premises.append((guess, fb))
        # Filter candidate codes to those consistent with the new premise.
        remaining = [code for code in remaining if get_feedback(code, guess) == fb]
        if fb == (pegs, 0):
            print(f"\n✅ Secret code found in {turn} turns!")
            return guess_history

    # Phase 2: Iterative inference guided by premises.
    # Choose next guesses from the remaining candidates based on consistency with all premises.
    while remaining:
        turn += 1
        best_guess = None
        best_score = float('inf')
        # For each candidate code, compute a score based on past premises
        for candidate in remaining:
            score = 0
            for (prev_guess, prev_fb) in premises:
                candidate_fb = get_feedback(candidate, prev_guess)
                # Increment score based on difference from recorded feedback.
                score += abs(candidate_fb[0] - prev_fb[0]) + abs(candidate_fb[1] - prev_fb[1])
            if score < best_score:
                best_score = score
                best_guess = candidate
        if best_guess is None:
            best_guess = random.choice(remaining)
        guess = best_guess
        guess_history.append(guess)
        fb = get_feedback(secret, guess)
        print(f"\nTurn {turn}: Guessed -> {list(guess)}")
        print(f"   ⚫ Siyah (Black): {fb[0]}")
        print(f"   ⚪ Beyaz (White): {fb[1]}")
        premises.append((guess, fb))
        # Filter remaining possibilities using all premises
        remaining = [code for code in remaining if all(get_feedback(code, g) == f for g, f in premises)]
        if fb == (pegs, 0):
            print(f"\n✅ Secret code found in {turn} turns!")
            return guess_history
        if not remaining:
            print("❌ No candidates remain. Terminating search.")
            break

    return guess_history

if __name__ == "__main__":
    try:
        user_input = input("Lütfen renkleri boşluk ile ayırarak giriniz (örnek: red red yellow green blue): ").strip()
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
    history = logical_inference_solver(secret_code, PEGS, COLORS, num_initial_guesses=3)
    
    print("\nLogical Inference Strategy Guess Sequence:")
    for i, g in enumerate(history, 1):
        print(f"Turn {i}: {list(g)}")