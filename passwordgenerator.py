import secrets
import string
import math

# Character groups
LOWER = string.ascii_lowercase
UPPER = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/|\\`~"
AMBIGUOUS = "Il1O0"   # characters to optionally exclude

def build_charset(use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous):
    s = ""
    if use_lower: s += LOWER
    if use_upper: s += UPPER
    if use_digits: s += DIGITS
    if use_symbols: s += SYMBOLS
    if exclude_ambiguous:
        s = "".join(ch for ch in s if ch not in AMBIGUOUS)
    return s

def entropy_bits(charset_len, length):
    if charset_len <= 1 or length <= 0:
        return 0.0
    return length * math.log2(charset_len)

def strength_label(bits):
    if bits < 28: return "Very weak"
    if bits < 36: return "Weak"
    if bits < 60: return "Moderate"
    if bits < 80: return "Strong"
    return "Very strong"

def generate_password(charset, length):
    return ''.join(secrets.choice(charset) for _ in range(length))

def prompt_bool(prompt, default=True):
    ans = input(f"{prompt} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
    if ans == "": return default
    return ans[0] == 'y'

def main():
    print("Simple Password Generator")
    try:
        length = int(input("Password length (e.g. 16): ").strip() or "16")
    except ValueError:
        print("Invalid length. Using 16.")
        length = 16
    if length < 1:
        print("Length must be positive. Using 16.")
        length = 16

    use_lower = prompt_bool("Include lowercase letters (a-z)?", True)
    use_upper = prompt_bool("Include uppercase letters (A-Z)?", True)
    use_digits = prompt_bool("Include digits (0-9)?", True)
    use_symbols = prompt_bool("Include symbols (!@#$...)?", True)
    exclude_amb = prompt_bool("Exclude ambiguous characters (I l 1 O 0)?", False)

    if not (use_lower or use_upper or use_digits or use_symbols):
        print("No character types selected. Enabling lowercase and digits.")
        use_lower = use_digits = True

    charset = build_charset(use_lower, use_upper, use_digits, use_symbols, exclude_amb)
    if not charset:
        print("Character set empty after options. Exiting.")
        return

    pwd = generate_password(charset, length)
    bits = entropy_bits(len(charset), length)
    strength = strength_label(bits)

    print("\nGenerated password:")
    print(pwd)
    print(f"\nDetails: length={length}, charset_size={len(charset)}, entropy={bits:.1f} bits, strength={strength}")

if __name__ == "__main__":
    main()
