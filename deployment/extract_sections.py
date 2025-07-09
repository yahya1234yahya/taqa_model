import csv

def extract_unique_sections():
    """
    Extract all unique "Section propriétaire" values from the three CSV files
    """
    print("Extracting unique sections from all CSV files...")
    
    sections = set()
    csv_files = ['disponibilite.csv', 'fiabilite.csv', 'process_safty.csv']
    
    for file_name in csv_files:
        print(f"Processing {file_name}...")
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    section = row.get('Section propriétaire', '').strip()
                    if section:  # Only add non-empty sections
                        sections.add(section)
        except FileNotFoundError:
            print(f"Warning: {file_name} not found, skipping...")
        except Exception as e:
            print(f"Error processing {file_name}: {e}")
    
    # Convert to sorted list for better display
    unique_sections = sorted(list(sections))
    
    print(f"\nFound {len(unique_sections)} unique sections:")
    print("="*50)
    
    for i, section in enumerate(unique_sections, 1):
        print(f"{i:2d}. {section}")
    
    # Save to CSV file
    with open('unique_sections.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Section_Code'])  # Header
        for section in unique_sections:
            writer.writerow([section])
    
    print(f"\nSaved to 'unique_sections.csv' with {len(unique_sections)} unique sections")
    
    return unique_sections

if __name__ == "__main__":
    sections = extract_unique_sections() 