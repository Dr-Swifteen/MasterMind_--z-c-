import sys

attemp = 0
colors = ['red', 'yellow', 'green', 'blue', 'pink', 'brown']

class Node:
    def __init__(self, color=None):
        self.color = color
        self.children = []

    def __repr__(self):
        return f"Node(color={self.color}, children={len(self.children)})"

def build_tree_bottom_up(max_level=5):
    global colors
    previous_level = [Node(color) for color in colors]
    for _ in range(max_level - 1):
        current_level = []
        for color in colors:
            node = Node(color)
            node.children = previous_level
            current_level.append(node)
        previous_level = current_level
    root = Node()
    root.children = previous_level
    return root

# ✅ Standard feedback function
def get_feedback(secret, guess):
    black = sum(s == g for s, g in zip(secret, guess))
    white = sum(min(secret.count(c), guess.count(c)) for c in set(guess)) - black
    return (black, white)

# ✅ Fixed DFS function
def dfs_check_sequence(node, path, target_sequence, level=0, max_level=5):
    global attemp
    if node.color:
        path.append(node.color)

    if level == max_level:
        attemp += 1
        if path == target_sequence:
            print("---------------------------------------------------------------------------------------------------------")
            print(f"✅ Match found: {path}")
            return True
        else:
            print(f"❌ No match found. Path reached: {path}")
            # ✅ Use the proper feedback function
            black, white = get_feedback(tuple(target_sequence), tuple(path))
            print(f" ⚫ Siyah: {black}")
            print(f" ⚪ Beyaz:  {white}")
        return False

    for child in node.children:
        if dfs_check_sequence(child, path.copy(), target_sequence, level + 1, max_level):
            return True

    return False

# ✅ Main execution
if __name__ == "__main__":
    tree_root = build_tree_bottom_up(5)
    try:
        a = input("Lütfen renkleri boşluk ile ayırarak giriniz ve hepsi küçük harfli olsun lütfen: ").strip()
        user_sequence = a.split()
        invalid_colors = [color for color in user_sequence if color not in colors]
        if invalid_colors:
            raise ValueError(f"❌ Hatalı renkler bulundu: {', '.join(invalid_colors)}")
        if len(user_sequence) != 5:
            raise IOError(f"Toplam renk sayısı 5 olmalıdır, sizin girdiniz: {len(user_sequence)}")
        print("✅ Kullanıcının girdiği tüm renkler geçerli!")
    except (ValueError, IOError) as e:
        print(e)
        sys.exit(0)

    found = dfs_check_sequence(tree_root, [], user_sequence)

    if not found:
        print("No matching sequence found. Your input might be incorrect or not found in the tree.")
    print("---------------------------------------------------------------------------------------------------------")
    print("Total attempt number is:", attemp)

