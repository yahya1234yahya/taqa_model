import csv

def extract_unique_sections():
    """ print("Extracting unique sections from all CSV files...") sections = set() csv_files = ['data/disponibilite.csv', 'data/fiabilite.csv', 'data/process_safty.csv']
    for file_name in csv_files:
        print(f"Processing {file_name}...")
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file) for row in reader:
                section = row.get('Section propriétaire', '').strip() if section:
                sections.add(section) except FileNotFoundError:
                print(f"Warning: {file_name} not found, skipping...")
                except Exception as e:
                    print(f"Error processing {file_name}: {e}") unique_sections = sorted(list(sections)) print(f"\nFound {len(unique_sections)} unique sections:") print("="*50)
                    for i, section in enumerate(unique_sections, 1):
                        print(f"{i:2d}. {section}") with open('data/unique_sections.csv', 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file) writer.writerow(['Section_Code']) for section in unique_sections:
                        writer.writerow([section]) print(f"\nSaved to 'data/unique_sections.csv' with {len(unique_sections)} unique sections") return unique_sections

                        if __name__ == "__main__":
                            sections = extract_unique_sections()