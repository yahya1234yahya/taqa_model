import csv
import re
from collections import defaultdict

def load_data():
    """Load and parse the process_safty CSV data"""
    data = []
    with open('process_safty.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def analyze_equipment_simple(data):
    """Analyze equipment - return only ID, description, and average process safety score"""
    
    equipment_scores = defaultdict(list)
    equipment_descriptions = {}
    
    # Collect scores for each equipment
    for record in data:
        equipment_id = record['Num_equipement']
        score = int(record['Process Safety'])
        equipment_desc = record['Description de l\'équipement']
        
        equipment_scores[equipment_id].append(score)
        equipment_descriptions[equipment_id] = equipment_desc
    
    # Calculate average scores
    equipment_analysis = []
    for equipment_id, scores in equipment_scores.items():
        avg_score = round(sum(scores) / len(scores), 2)
        
        equipment_analysis.append({
            'Equipment_ID': equipment_id,
            'Equipment_Description': equipment_descriptions[equipment_id],
            'Average_Process_Safety_Score': avg_score
        })
    
    # Sort by average score (highest first)
    equipment_analysis.sort(key=lambda x: x['Average_Process_Safety_Score'], reverse=True)
    
    print("=== PROCESS SAFETY EQUIPMENT ANALYSIS ===")
    print(f"Total unique equipment: {len(equipment_analysis)}")
    print(f"\nTop 20 equipment by average process safety score:")
    print(f"{'Equipment ID':<40} {'Average Score':<15} {'Description'}")
    print("-" * 100)
    
    for i, equipment in enumerate(equipment_analysis[:20]):
        desc = equipment['Equipment_Description'][:45] + "..." if len(equipment['Equipment_Description']) > 45 else equipment['Equipment_Description']
        print(f"{equipment['Equipment_ID']:<40} {equipment['Average_Process_Safety_Score']:<15} {desc}")
    
    return equipment_analysis

def analyze_severe_words(data):
    """Analyze severe words and their average process safety scores"""
    
    # Expanded keywords that indicate severity (focusing on process safety aspects)
    severe_keywords = [
        # Core severity terms
        'sévère', 'severe', 'grave', 'important', 'importante', 'critique', 'critical',
        'urgent', 'danger', 'dangereuse', 'dangereux', 'risque', 'risk',
        
        # Safety-specific terms
        'sécurité', 'safety', 'sûreté', 'accident', 'incident', 'blessure', 'injury',
        'explosion', 'incendie', 'fire', 'toxique', 'toxic', 'poison', 'empoisonnement',
        'asphyxie', 'suffocation', 'brûlure', 'burn', 'exposition', 'exposure',
        
        # Failure and breakdown terms
        'défaillance', 'panne', 'failure', 'breakdown', 'arrêt', 'stop', 'stoppage',
        'blocage', 'blocked', 'bloqué', 'immobilisé', 'hors service', 'out of service',
        'indisponible', 'unavailable', 'dysfonctionnement', 'malfunction',
        
        # Process safety hazards
        'fuite', 'leak', 'leakage', 'fuite importante', 'major leak', 'suintement',
        'écoulement', 'infiltration', 'étanchéité', 'sealing', 'percement',
        'perforation', 'percé', 'troué', 'hole', 'rupture', 'fracture',
        
        # Pressure and containment
        'surpression', 'overpressure', 'dépression', 'under-pressure', 'pression',
        'pressure', 'explosion', 'blast', 'éclatement', 'burst', 'soupape',
        'relief valve', 'valve de sécurité', 'safety valve',
        
        # Temperature issues
        'surchauffe', 'overheating', 'échauffement', 'heating', 'température élevée',
        'high temperature', 'chaud', 'hot', 'brûlant', 'burning', 'thermal',
        'refroidissement', 'cooling', 'température', 'temp', 'cryogénique', 'cryogenic',
        
        # Chemical hazards
        'corrosion', 'corrosive', 'acide', 'acid', 'base', 'alcalin', 'alkaline',
        'réactif', 'reactive', 'instable', 'unstable', 'polymérisation', 'polymerization',
        'décomposition', 'decomposition', 'combustible', 'flammable', 'inflammable',
        
        # Mechanical hazards
        'vibration', 'vibrations', 'oscillation', 'trembling', 'instabilité',
        'instability', 'déséquilibre', 'unbalance', 'désalignement', 'misalignment',
        'jeu excessif', 'excessive play', 'usure', 'wear', 'usé', 'worn',
        'fatigue', 'fracture', 'cassure', 'break', 'casse',
        
        # Electrical hazards
        'court-circuit', 'short circuit', 'surtension', 'overvoltage', 'sous-tension',
        'undervoltage', 'électrique', 'electrical', 'isolement', 'insulation',
        'décharge', 'discharge', 'arc', 'étincelle', 'spark', 'électrocution',
        'electrocution', 'choc électrique', 'electric shock',
        
        # Environmental hazards
        'contamination', 'contaminé', 'contaminated', 'pollution', 'pollué',
        'polluted', 'impureté', 'impurity', 'sale', 'dirty', 'encrassement',
        'fouling', 'dépôt', 'deposit', 'résidu', 'residue', 'émission', 'emission',
        
        # Noise and vibration
        'bruit', 'noise', 'bruit anormal', 'abnormal noise', 'bruit excessif',
        'excessive noise', 'grincement', 'grinding', 'claquement', 'clicking',
        'sifflement', 'whistling', 'bourdonnement', 'humming', 'décibel', 'decibel',
        
        # Process deviations
        'écart', 'deviation', 'hors limite', 'out of limit', 'dépassement', 'exceeding',
        'anormal', 'abnormal', 'irrégulier', 'irregular', 'fluctuation', 'variation',
        'dérive', 'drift', 'instable', 'unstable', 'oscillation',
        
        # Emergency and alarms
        'alarme', 'alarm', 'alerte', 'alert', 'warning', 'avertissement',
        'emergency', 'urgence', 'secours', 'rescue', 'évacuation', 'evacuation',
        'arrêt d\'urgence', 'emergency stop', 'trip', 'déclenchement', 'shutdown',
        
        # Maintenance urgency
        'réparation', 'repair', 'maintenance', 'intervention', 'remplacement',
        'replacement', 'changement', 'change', 'révision', 'overhaul',
        'inspection', 'contrôle', 'check', 'vérification', 'verification',
        
        # Human factors
        'erreur', 'error', 'faute', 'mistake', 'négligence', 'negligence',
        'formation', 'training', 'procédure', 'procedure', 'consigne', 'instruction',
        'epi', 'ppe', 'équipement de protection', 'protective equipment',
        
        # Containment and isolation
        'confinement', 'containment', 'isolement', 'isolation', 'coupure', 'cut-off',
        'interruption', 'perturbation', 'disturbance', 'trouble', 'problème', 'problem',
        'fermeture', 'closure', 'ouverture', 'opening', 'vanne', 'valve',
        
        # Structural integrity
        'fissure', 'crack', 'cracking', 'fissuré', 'cracked', 'casse', 'break',
        'cassé', 'broken', 'déformation', 'deformation', 'déformé', 'deformed',
        'endommagé', 'damaged', 'détérioration', 'deterioration', 'dégradation',
        'degradation', 'usure', 'wear', 'érosion', 'erosion',
        
        # Operational hazards
        'surcharge', 'overload', 'sous-charge', 'underload', 'débit', 'flow',
        'niveau', 'level', 'capacité', 'capacity', 'limite', 'limit',
        'maximum', 'minimum', 'seuil', 'threshold', 'tolérance', 'tolerance'
    ]
    
    # Track scores for each word
    word_scores = defaultdict(list)
    
    for record in data:
        description = record['Description'].lower() if record['Description'] else ""
        score = int(record['Process Safety'])
        
        # Check for each keyword
        for keyword in severe_keywords:
            if keyword in description:
                word_scores[keyword].append(score)
    
    # Calculate average scores for words
    word_analysis = []
    for word, scores in word_scores.items():
        if len(scores) > 0:  # Only include words that were found
            avg_score = round(sum(scores) / len(scores), 2)
            word_analysis.append({
                'Word': word,
                'Average_Process_Safety_Score': avg_score,
                'Occurrences': len(scores)
            })
    
    # Sort by average score (highest first)
    word_analysis.sort(key=lambda x: x['Average_Process_Safety_Score'], reverse=True)
    
    print("\n=== PROCESS SAFETY SEVERE WORDS ANALYSIS ===")
    print(f"Total severe words found: {len(word_analysis)}")
    print(f"\nSevere words by average process safety score:")
    print(f"{'Word':<25} {'Average Score':<15} {'Occurrences'}")
    print("-" * 60)
    
    for word_data in word_analysis:
        print(f"{word_data['Word']:<25} {word_data['Average_Process_Safety_Score']:<15} {word_data['Occurrences']}")
    
    return word_analysis

def export_focused_results(equipment_analysis, word_analysis):
    """Export simplified process safety results to CSV files"""
    
    # Export equipment with just ID, description, and average process safety score
    with open('equipment_process_safety_simple.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Equipment_ID', 'Equipment_Description', 'Average_Process_Safety_Score'])
        
        for equipment in equipment_analysis:
            writer.writerow([
                equipment['Equipment_ID'],
                equipment['Equipment_Description'],
                equipment['Average_Process_Safety_Score']
            ])
    
    # Export words with just word and average process safety score
    with open('severe_words_process_safety_simple.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Word', 'Average_Process_Safety_Score', 'Occurrences'])
        
        for word_data in word_analysis:
            writer.writerow([
                word_data['Word'],
                word_data['Average_Process_Safety_Score'],
                word_data['Occurrences']
            ])
    
    print("\n=== PROCESS SAFETY EXPORT COMPLETE ===")
    print("Simplified process safety files created:")
    print("- equipment_process_safety_simple.csv (Equipment ID, Description, Average Process Safety Score)")
    print("- severe_words_process_safety_simple.csv (Word, Average Process Safety Score, Occurrences)")

def main():
    """Main analysis function for process safety data"""
    
    print("Starting Process Safety Analysis...")
    print("=" * 60)
    
    try:
        # Load data
        data = load_data()
        print(f"Loaded {len(data)} records from process_safty.csv")
        
        # Analyze equipment (simple version)
        equipment_analysis = analyze_equipment_simple(data)
        
        # Analyze severe words
        word_analysis = analyze_severe_words(data)
        
        # Export simplified results
        export_focused_results(equipment_analysis, word_analysis)
        
        print("\n" + "=" * 60)
        print("Process Safety analysis complete!")
        print(f"\nSummary:")
        print(f"- Analyzed {len(equipment_analysis)} unique equipment items")
        print(f"- Found {len(word_analysis)} severe words with process safety scores")
        print(f"- Generated simplified CSV files for ML modeling")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 