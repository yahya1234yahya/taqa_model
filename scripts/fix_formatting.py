import os
import re
import ast
import glob

def fix_python_formatting(file_path):
    """Fix Python file formatting that got mangled"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # If the file is all on one line, we need to restore proper formatting
        if '\n' not in content or content.count('\n') < 10:
            print(f"Fixing formatting for: {file_path}")
            
            # Add newlines after common Python keywords and patterns
            fixed_content = content
            
            # Add newlines after import statements
            fixed_content = re.sub(r'(import [^;]+?)(import|from|def|class|if|while|for|try|except|with)', r'\1\n\2', fixed_content)
            fixed_content = re.sub(r'(from [^;]+?)(import|from|def|class|if|while|for|try|except|with)', r'\1\n\2', fixed_content)
            
            # Add newlines before function and class definitions
            fixed_content = re.sub(r'(\s*)(def |class )', r'\n\n\1\2', fixed_content)
            
            # Add newlines after function/class definitions (after the colon)
            fixed_content = re.sub(r'(def [^:]+:)(\s*)', r'\1\n    ', fixed_content)
            fixed_content = re.sub(r'(class [^:]+:)(\s*)', r'\1\n    ', fixed_content)
            
            # Add newlines after control structures
            fixed_content = re.sub(r'(if [^:]+:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(elif [^:]+:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(else:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(for [^:]+:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(while [^:]+:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(try:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(except[^:]*:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(finally:)(\s*)', r'\1\n        ', fixed_content)
            fixed_content = re.sub(r'(with [^:]+:)(\s*)', r'\1\n        ', fixed_content)
            
            # Add newlines after return, print, etc.
            fixed_content = re.sub(r'(return [^;]+?)(\s*)(def|class|if|while|for|try|except|print|return)', r'\1\n\n    \3', fixed_content)
            fixed_content = re.sub(r'(print\([^)]+\))(\s*)(def|class|if|while|for|try|except|print|return)', r'\1\n    \3', fixed_content)
            
            # Fix indentation issues
            lines = fixed_content.split('\n')
            fixed_lines = []
            indent_level = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    fixed_lines.append('')
                    continue
                
                # Adjust indent level based on line content
                if line.startswith(('def ', 'class ')):
                    indent_level = 0
                    fixed_lines.append('    ' * indent_level + line)
                    indent_level = 1
                elif line.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ')):
                    if line.endswith(':'):
                        fixed_lines.append('    ' * indent_level + line)
                        indent_level += 1
                    else:
                        fixed_lines.append('    ' * indent_level + line)
                elif line.startswith(('return ', 'break', 'continue', 'pass')):
                    fixed_lines.append('    ' * indent_level + line)
                    if line.startswith('return ') and indent_level > 1:
                        indent_level = max(1, indent_level - 1)
                elif line.startswith('import ') or line.startswith('from '):
                    indent_level = 0
                    fixed_lines.append(line)
                else:
                    fixed_lines.append('    ' * indent_level + line)
            
            fixed_content = '\n'.join(fixed_lines)
            
            # Clean up excessive newlines
            fixed_content = re.sub(r'\n{3,}', '\n\n', fixed_content)
            
            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return True
        else:
            print(f"File already properly formatted: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def restore_focused_analysis():
    """Restore the focused_analysis.py file specifically"""
    focused_content = '''import csv
import re
from collections import defaultdict

def load_data():
    data = []
    with open('data/disponibilite.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def analyze_equipment_simple(data):
    equipment_scores = defaultdict(list)
    equipment_descriptions = {}
    
    for record in data:
        equipment_id = record['Num_equipement']
        score = int(record['Disponibilté'])
        equipment_desc = record['Description de l\\'équipement']
        
        equipment_scores[equipment_id].append(score)
        equipment_descriptions[equipment_id] = equipment_desc
    
    equipment_analysis = []
    for equipment_id, scores in equipment_scores.items():
        avg_score = round(sum(scores) / len(scores), 2)
        equipment_analysis.append({
            'Equipment_ID': equipment_id,
            'Equipment_Description': equipment_descriptions[equipment_id],
            'Average_Score': avg_score
        })
    
    equipment_analysis.sort(key=lambda x: x['Average_Score'], reverse=True)
    
    print("=== EQUIPMENT ANALYSIS ===")
    print(f"Total unique equipment: {len(equipment_analysis)}")
    print(f"\\nTop 20 equipment by average availability score:")
    print(f"{'Equipment ID':<40} {'Average Score':<15} {'Description'}")
    print("-" * 100)
    
    for i, equipment in enumerate(equipment_analysis[:20]):
        desc = equipment['Equipment_Description'][:45] + "..." if len(equipment['Equipment_Description']) > 45 else equipment['Equipment_Description']
        print(f"{equipment['Equipment_ID']:<40} {equipment['Average_Score']:<15} {desc}")
    
    return equipment_analysis

def analyze_severe_words(data):
    severe_keywords = [
        'sévère', 'severe', 'grave', 'important', 'importante', 'critique', 'critical',
        'urgent', 'danger', 'dangereuse', 'dangereux', 'risque', 'risk',
        'défaillance', 'panne', 'failure', 'breakdown', 'arrêt', 'stop', 'stoppage',
        'blocage', 'blocked', 'bloqué', 'immobilisé', 'hors service', 'out of service',
        'indisponible', 'unavailable', 'dysfonctionnement', 'malfunction',
        'fuite', 'leak', 'leakage', 'fuite importante', 'major leak', 'suintement',
        'écoulement', 'infiltration', 'étanchéité', 'sealing', 'percement',
        'perforation', 'percé', 'troué', 'hole', 'surchauffe', 'overheating',
        'échauffement', 'heating', 'température élevée', 'high temperature',
        'chaud', 'hot', 'brûlant', 'burning', 'thermal', 'refroidissement',
        'cooling', 'température', 'temp', 'vibration', 'vibrations',
        'oscillation', 'trembling', 'instabilité', 'instability',
        'déséquilibre', 'unbalance', 'désalignement', 'misalignment',
        'jeu excessif', 'excessive play', 'usure', 'wear', 'usé', 'worn',
        'bruit', 'noise', 'bruit anormal', 'abnormal noise',
        'bruit excessif', 'excessive noise', 'grincement', 'grinding',
        'claquement', 'clicking', 'sifflement', 'whistling',
        'bourdonnement', 'humming', 'fissure', 'crack', 'cracking',
        'fissuré', 'cracked', 'casse', 'break', 'cassé', 'broken',
        'rupture', 'fracture', 'déformation', 'deformation',
        'déformé', 'deformed', 'endommagé', 'damaged',
        'détérioration', 'deterioration', 'dégradation', 'degradation',
        'corrosion', 'rouille', 'rust', 'performance', 'rendement',
        'efficiency', 'efficacité', 'faible', 'low', 'réduit', 'reduced',
        'diminué', 'decreased', 'insuffisant', 'insufficient',
        'mauvais', 'bad', 'poor', 'déficient', 'deficient',
        'court-circuit', 'short circuit', 'surtension', 'overvoltage',
        'sous-tension', 'undervoltage', 'électrique', 'electrical',
        'isolement', 'insulation', 'décharge', 'discharge', 'arc',
        'étincelle', 'spark', 'contamination', 'contaminé', 'contaminated',
        'pollution', 'pollué', 'polluted', 'impureté', 'impurity',
        'sale', 'dirty', 'encrassement', 'fouling', 'dépôt', 'deposit',
        'résidu', 'residue', 'instable', 'unstable', 'fluctuation',
        'variation', 'oscillation', 'dérive', 'drift', 'écart', 'deviation',
        'hors limite', 'out of limit', 'dépassement', 'exceeding',
        'anormal', 'abnormal', 'irrégulier', 'irregular', 'alarme', 'alarm',
        'alerte', 'alert', 'warning', 'avertissement', 'emergency', 'urgence',
        'secours', 'rescue', 'évacuation', 'evacuation', 'réparation', 'repair',
        'maintenance', 'intervention', 'remplacement', 'replacement',
        'changement', 'change', 'révision', 'overhaul', 'inspection',
        'contrôle', 'check', 'vérification', 'verification',
        'arrêt d\\'urgence', 'emergency stop', 'trip', 'déclenchement',
        'shutdown', 'fermeture', 'closure', 'isolement', 'isolation',
        'coupure', 'cut-off', 'interruption', 'perturbation', 'disturbance',
        'trouble', 'problème', 'problem', 'aggravation', 'worsening',
        'détérioration', 'deteriorating', 'évolution', 'evolution',
        'progression', 'augmentation', 'increase', 'croissance', 'growth',
        'extension', 'propagation', 'spread'
    ]
    
    word_scores = defaultdict(list)
    
    for record in data:
        description = record['Description'].lower()
        score = int(record['Disponibilté'])
        
        for keyword in severe_keywords:
            if keyword in description:
                word_scores[keyword].append(score)
    
    word_analysis = []
    for word, scores in word_scores.items():
        if len(scores) > 0:
            avg_score = round(sum(scores) / len(scores), 2)
            word_analysis.append({
                'Word': word,
                'Average_Score': avg_score,
                'Occurrences': len(scores)
            })
    
    word_analysis.sort(key=lambda x: x['Average_Score'], reverse=True)
    
    print("\\n=== SEVERE WORDS ANALYSIS ===")
    print(f"Total severe words found: {len(word_analysis)}")
    print(f"\\nSevere words by average availability score:")
    print(f"{'Word':<25} {'Average Score':<15} {'Occurrences'}")
    print("-" * 60)
    
    for word_data in word_analysis:
        print(f"{word_data['Word']:<25} {word_data['Average_Score']:<15} {word_data['Occurrences']}")
    
    return word_analysis

def export_focused_results(equipment_analysis, word_analysis):
    with open('data/equipment_simple.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Equipment_ID', 'Equipment_Description', 'Average_Score'])
        for equipment in equipment_analysis:
            writer.writerow([
                equipment['Equipment_ID'],
                equipment['Equipment_Description'],
                equipment['Average_Score']
            ])
    
    with open('data/severe_words_simple.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Word', 'Average_Score', 'Occurrences'])
        for word_data in word_analysis:
            writer.writerow([
                word_data['Word'],
                word_data['Average_Score'],
                word_data['Occurrences']
            ])
    
    print("\\n=== EXPORT COMPLETE ===")
    print("Simplified files created:")
    print("- equipment_simple.csv (Equipment ID, Description, Average Score)")
    print("- severe_words_simple.csv (Word, Average Score, Occurrences)")

def main():
    print("Starting Focused Analysis...")
    print("=" * 60)
    
    try:
        data = load_data()
        print(f"data/Loaded {len(data)} records from disponibilite.csv")
        
        equipment_analysis = analyze_equipment_simple(data)
        word_analysis = analyze_severe_words(data)
        
        export_focused_results(equipment_analysis, word_analysis)
        
        print("\\n" + "=" * 60)
        print("Focused analysis complete!")
        print(f"\\nSummary:")
        print(f"- Analyzed {len(equipment_analysis)} unique equipment items")
        print(f"- Found {len(word_analysis)} severe words with scores")
        print(f"- Generated simplified CSV files for ML modeling")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open('focused_analysis.py', 'w', encoding='utf-8') as f:
        f.write(focused_content)
    print("Restored focused_analysis.py")

def main():
    """Fix all Python files that got mangled"""
    print("FIXING PYTHON FILE FORMATTING")
    print("=" * 50)
    
    # First, restore the focused_analysis.py file specifically
    restore_focused_analysis()
    
    # Get all Python files
    python_files = glob.glob("*.py")
    
    fixed_count = 0
    total_count = len(python_files)
    
    for py_file in python_files:
        if py_file == 'focused_analysis.py':
            continue  # Already fixed
        if fix_python_formatting(py_file):
            fixed_count += 1
    
    print(f"\nSUMMARY:")
    print(f"Total files: {total_count}")
    print(f"Files fixed: {fixed_count + 1}")  # +1 for focused_analysis.py
    print(f"Files already correct: {total_count - fixed_count - 1}")
    print("\nPython files have been restored to proper formatting!")

if __name__ == "__main__":
    main()
