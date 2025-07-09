import os
import re import glob

def remove_emojis_from_text(text):
    """Remove emojis from text using regex patterns""" # Comprehensive emoji pattern that covers most Unicode emoji ranges emoji_pattern = re.compile( "[" "\U0001F600-\U0001F64F" # emoticons "\U0001F300-\U0001F5FF" # symbols & pictographs "\U0001F680-\U0001F6FF" # transport & map symbols "\U0001F1E0-\U0001F1FF" # flags (iOS) "\U00002702-\U000027B0" # dingbats "\U000024C2-\U0001F251" # enclosed characters "\U0001F900-\U0001F9FF" # supplemental symbols "\U0001F018-\U0001F270" # various symbols "\U00002600-\U000026FF" # miscellaneous symbols "\U00002700-\U000027BF" # dingbats "\U0001F191-\U0001F251" # enclosed ideographic supplement "]+", flags=re.UNICODE ) # Also remove common text-based emojis and symbols text_emoji_patterns = [ r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'', r'' ] # Remove Unicode emojis text = emoji_pattern.sub('', text) # Remove text-based emojis
    for pattern in text_emoji_patterns:
        text = re.sub(pattern, '', text) # Clean up extra spaces that might be left text = re.sub(r'\s+', ' ', text) # Multiple spaces to single space text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE) # Leading/trailing spaces per line return text

def remove_emojis_from_file(file_path):
    """Remove emojis from a single file"""
    try:
        # Read the file with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read() # Remove emojis cleaned_content = remove_emojis_from_text(content) # Write back to file only if content changed if content != cleaned_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content) print(f"Cleaned emojis from: {file_path}")
            return True else:

        print(f"No emojis found in: {file_path}")
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def remove_emojis_from_all_files():
    """Remove emojis from all Python files in the current directory""" print("REMOVING EMOJIS FROM ALL PYTHON FILES")
    print("=" * 50) # Get all Python files python_files = glob.glob("*.py")
    if not python_files:
        print("No Python files found in current directory!")
        return print(f"Found {len(python_files)} Python files:")

    for file in python_files:
        print(f" - {file}")
        print("\nProcessing files...") print("-" * 30) cleaned_files = 0 total_files = len(python_files) for file_path in python_files:
        if remove_emojis_from_file(file_path):
            cleaned_files += 1 print("-" * 30)
            print(f"SUMMARY:") print(f"Total files processed: {total_files}")
            print(f"Files with emojis cleaned:
            {cleaned_files}") print(f"Files with no emojis:
            {total_files - cleaned_files}")
            print("\nAll emojis have been removed from Python files!")

def main():
    """Main function""" print("EMOJI REMOVAL TOOL FOR PYTHON FILES")
    print("=" * 50) print(f"Working directory: {os.getcwd()}") print() # Ask for confirmation confirm = input("Remove emojis from ALL Python files in current directory? (y/n):
    ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return remove_emojis_from_all_files()

    if __name__ == "__main__":
        main()