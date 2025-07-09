import os
import re import glob

def remove_comments_from_file(file_path):
    """Remove comments from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read() lines = content.split('\n') cleaned_lines = [] in_multiline_string = False string_delimiter = None for line in lines:
            original_line = line cleaned_line = line triple_double = line.count('"""') if (line.strip().startswith('"""') or line.strip().startswith("'''")) and in_multiline_string:
            continue elif in_multiline_string:
            continue if in_multiline_string:
            continue in_string = False string_char = None comment_pos = -1 i = 0 while i < len(line):
            char = line[i] if not in_string and char == '#':
            comment_pos = i break elif char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
            if not in_string:
                in_string = True string_char = char elif char == string_char:
                in_string = False string_char = None i += 1 if comment_pos >= 0:
                cleaned_line = line[:comment_pos].rstrip() if cleaned_line.strip() or original_line.strip() == '':
                cleaned_lines.append(cleaned_line) cleaned_content = '\n'.join(cleaned_lines) cleaned_content = re.sub(r'(\n\s*def\s+\w+\([^)]*\):\s*\n\s*""".*?"""\s*\n)', r'\1', cleaned_content, flags=re.DOTALL) cleaned_content = re.sub(r'(\n\s*class\s+\w+[^:]*:\s*\n\s*""".*?"""\s*\n)', r'\1', cleaned_content, flags=re.DOTALL) cleaned_content = re.sub(r'(\n\s*def\s+\w+\([^)]*\):\s*\n\s*\'\'\'.*?\'\'\'\s*\n)', r'\1', cleaned_content, flags=re.DOTALL) cleaned_content = re.sub(r'(\n\s*class\s+\w+[^:]*:\s*\n\s*\'\'\'.*?\'\'\'\s*\n)', r'\1', cleaned_content, flags=re.DOTALL) with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content) print(f" Cleaned: {os.path.basename(file_path)}") return True

                except Exception as e:
                    print(f" Error cleaning {file_path}: {e}")
                    return False

def main():
    """Remove comments from all Python files""" print(" REMOVING COMMENTS FROM ALL PYTHON FILES")
    print("="*50) py_files = glob.glob("*.py") success_count = 0 total_count = len(py_files)
    for py_file in py_files:
        if remove_comments_from_file(py_file):
            success_count += 1 print(f"\n SUMMARY:")
            print(f"Total files: {total_count}") print(f"Successfully cleaned: {success_count}")
            print(f"Failed: {total_count - success_count}") if success_count == total_count:
            print("\n All Python files have been cleaned of comments!") else:
            print(f"\n Some files could not be cleaned.")
            if __name__ == "__main__":
                main()