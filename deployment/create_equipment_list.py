import csv

def create_equipment_list():
    """
    Create a simple CSV with just Equipment ID and Equipment Name
    """
    print("Creating equipment list...")
    
    # Read the existing equipment data
    equipment_list = []
    
    with open('equipment_simple.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            equipment_list.append({
                'Equipment_ID': row['Equipment_ID'],
                'Equipment_Name': row['Equipment_Description']
            })
    
    # Sort by equipment name for easier browsing
    equipment_list.sort(key=lambda x: x['Equipment_Name'])
    
    # Write to new CSV file
    with open('equipment_list.csv', 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['Equipment_ID', 'Equipment_Name']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(equipment_list)
    
    print(f"Created equipment_list.csv with {len(equipment_list)} equipment items")
    print("File contains: Equipment_ID, Equipment_Name")
    
    # Show first few entries
    print("\nFirst 10 entries:")
    for i, eq in enumerate(equipment_list[:10]):
        print(f"{i+1}. {eq['Equipment_ID']} | {eq['Equipment_Name']}")

if __name__ == "__main__":
    create_equipment_list() 