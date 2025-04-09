
import itertools
import random
import sys
from functools import lru_cache

# ------------------------------
# Configuration and Utilities
# ------------------------------
COLORS = ['red', 'yellow', 'green', 'blue', 'pink', 'brown']
PEGS = 5

@lru_cache(maxsize=None)
def get_feedback(secret, guess):
    """
    Returns Mastermind feedback as (black, white) where:
      - black: number of pegs that are correct in both color and position.
      - white: number of pegs with correct color but in the wrong position.
    Both `secret` and `guess` are tuples of strings.
    """
    black = sum(s == g for s, g in zip(secret, guess))
    white = sum(min(secret.count(c), guess.count(c)) for c in set(guess)) - black
    return (black, white)

# ------------------------------
# CNF Representation (Simplified)
# ------------------------------
# We represent each literal as a string.
# For example:
#   "Color(3, 'red')" means: The 3rd peg is red.
#   "~Color(3, 'red')" means: The 3rd peg is NOT red.
#
# A clause is a set of literals (the disjunction of those literals),
# and the entire CNF is a list of such clauses (all of which must be true).

def code_satisfies_cnf(code, cnf):
    """
    Given a candidate code (tuple of length PEGS) and a CNF (list of clauses),
    return True if for every clause at least one literal is true for the code.
    For literal evaluation:
       - "Color(i, 'c')" is True if code[i-1] == c.
       - "~Color(i, 'c')" is True if code[i-1] != c.
    """
    for clause in cnf:
        clause_sat = False
        for literal in clause:
            if literal.startswith("~"):
                # negative literal: e.g., "~Color(3, 'red')"
                pos_literal = literal[1:]  # remove "~"
                try:
                    inside = pos_literal[len("Color("):-1]  # extract content, e.g., "3, 'red'"
                    i_str, col_str = inside.split(",")
                    i = int(i_str.strip())
                    c = col_str.strip().strip("'")
                except:
                    continue
                if code[i-1] != c:
                    clause_sat = True
                    break
            else:
                # positive literal: e.g., "Color(1, 'blue')"
                try:
                    inside = literal[len("Color("):-1]
                    i_str, col_str = inside.split(",")
                    i = int(i_str.strip())
                    c = col_str.strip().strip("'")
                except:
                    continue
                if code[i-1] == c:
                    clause_sat = True
                    break
        if not clause_sat:
            return False
    return True

def derive_simple_cnf_constraints(guess, fb):
    """
    Given a guess (tuple) and its feedback (black, white),
    derive some simple CNF clauses.
    
    For demonstration:
      - If the guess results in 0 black pegs, for each position we add a clause 
        saying that the color at that position cannot be the guessed color.
      
      - (A full CNF encoding would also encode the number of white pegs.)
    """
    clauses = []
    black, white = fb
    
    # Only add the negative clauses when no peg is correct in its position.
    if black == 0:
        for i in range(PEGS):
            clause = {f"~Color({i+1}, '{guess[i]}')"}
            clauses.append(clause)
    # (Optionally, other types of clauses could be added if needed.)
    
    return clauses

# ------------------------------
# Logical Inference Solver (CNF-based)
# ------------------------------
def logical_inference_solver_CNF(secret, num_initial_guesses=3):
    """
    A Mastermind solver using a logical inference approach with a simplified CNF encoding.
    
    Steps:
      1) Random Exploration: Make num_initial_guesses random guesses.
         For each guess, record (guess, feedback) as a "premise" and (if applicable) derive CNF clauses.
         The candidate space is filtered to only those that yield the same feedback for each guess.
      2) Inference Phase: Choose further guesses from the remaining candidates.
         (Here we simply select a random candidate that satisfies all premises.)
      3) The premises are used to filter the candidates.
      
    Returns a list of guesses made.
    """
    # Generate the full space of codes.
    all_codes = list(itertools.product(COLORS, repeat=PEGS))
    remaining = all_codes.copy()
    
    # The premises: a list of (guess, feedback) pairs.
    premises = []
    # The CNF clauses (initially empty).
    cnf_premises = []
    guess_history = []
    
    turn = 0
    
    # --- Phase 1: Random Exploration ---
    for _ in range(num_initial_guesses):
        if not remaining:
            print("❌ No candidates remain—terminating.")
            return guess_history
        turn += 1
        guess = random.choice(remaining)
        guess_history.append(guess)
        fb = get_feedback(secret, guess)
        print(f"\nTurn {turn}: Guessed -> {list(guess)}")
        print(f"   ⚫ Siyah (Black): {fb[0]}")
        print(f"   ⚪ Beyaz (White): {fb[1]}")
        if fb == (PEGS, 0):
            print(f"\n✅ Secret code found in {turn} guesses!")
            return guess_history
        
        premises.append((guess, fb))
        # Derive additional CNF constraints if possible.
        new_clauses = derive_simple_cnf_constraints(guess, fb)
        cnf_premises.extend(new_clauses)
        # Filter candidates: candidate must satisfy every recorded premise AND the CNF.
        remaining = [code for code in remaining if all(get_feedback(code, g) == f for g, f in premises)]
        # Optionally, also filter candidates by checking the CNF:
        remaining = [code for code in remaining if code_satisfies_cnf(code, cnf_premises)]
    
    # --- Phase 2: Inference Phase ---
    # Now we assume that the premises (from initial guesses) have narrowed the candidate set.
    # We select further guesses from the candidates.
    while remaining:
        turn += 1
        # Here we simply select a candidate from the remaining space.
        # (One could also use a scoring function, for example, by checking
        # the candidate's consistency with previous premises.)
        guess = random.choice(remaining)
        guess_history.append(guess)
        fb = get_feedback(secret, guess)
        print(f"\nTurn {turn}: Guessed -> {list(guess)}")
        print(f"   ⚫ Siyah (Black): {fb[0]}")
        print(f"   ⚪ Beyaz (White): {fb[1]}")
        
        if fb == (PEGS, 0):
            print(f"\n✅ Secret code found in {turn} guesses!")
            return guess_history
        
        premises.append((guess, fb))
        new_clauses = derive_simple_cnf_constraints(guess, fb)
        cnf_premises.extend(new_clauses)
        
        remaining = [code for code in remaining if all(get_feedback(code, g) == f for g, f in premises)]
        remaining = [code for code in remaining if code_satisfies_cnf(code, cnf_premises)]
        
        if not remaining:
            print("❌ No candidates remain. Possibly the constraints are too strong or incomplete encoding.")
            break
    
    return guess_history

# ------------------------------
# Main Input/Output Routine
# ------------------------------
if __name__ == "__main__":
    try:
        user_input = input("Lütfen renkleri boşluk ile ayırarak giriniz (örnek: red red yellow green blue): ").strip()
        user_sequence = user_input.split()
        invalid_colors = [c for c in user_sequence if c not in COLORS]
        if invalid_colors:
            raise ValueError(f"❌ Hatalı renkler bulundu: {', '.join(invalid_colors)}")
        if len(user_sequence) != PEGS:
            raise IOError(f"Toplam renk sayısı {PEGS} olmalıdır, girilen sayı: {len(user_sequence)}")
        print("✅ Kullanıcının girdiği tüm renkler geçerli!")
    except (ValueError, IOError) as e:
        print(e)
        sys.exit(0)
    
    secret_code = tuple(user_sequence)
    history = logical_inference_solver_CNF(secret_code, num_initial_guesses=3)
    
    print("\nCNF-Based Logical Inference Guess Sequence:")
    for i, g in enumerate(history, 1):
        print(f"Turn {i}: {list(g)}")
