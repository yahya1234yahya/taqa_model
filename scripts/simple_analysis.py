import csv
import re from collections
import defaultdict, Counter
import json

def load_data():
    """Load and parse the CSV data""" data = [] with open('data/disponibilite.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file) for row in reader:
    data.append(row) return data

def extract_severe_descriptions(data):
    """Extract descriptions containing severe-related keywords""" severe_keywords = [ 'sévère', 'severe', 'grave', 'important', 'importante', 'critique', 'critical', 'urgent', 'danger', 'fuite importante', 'défaillance', 'panne', 'arrêt', 'bruit anormal', 'vibration', 'surchauffe', 'échauffement', 'percement', 'fissure', 'casse', 'détérioration', 'aggravation' ] severe_records = [] keyword_counts = Counter() for record in data:
    description = record['Description'].lower() found_keywords = [] for keyword in severe_keywords:
    if keyword in description:
        found_keywords.append(keyword) keyword_counts[keyword] += 1 if found_keywords:
        severe_records.append({ 'Description': record['Description'], 'Availability_Score': int(record['Disponibilté']), 'Equipment_Description': record['Description de l\'équipement'], 'Section': record['Section propriétaire'], 'Date': record['Date de détéction de l\'anomalie'], 'Found_Keywords': found_keywords }) print("=== SEVERE DESCRIPTIONS ANALYSIS ===")
        print(f"Total records: {len(data)}") print(f"Severe records found: {len(severe_records)}") print(f"Percentage of severe issues: {len(severe_records)/len(data)*100:.1f}%") score_distribution = Counter() for record in severe_records:
        score_distribution[record['Availability_Score']] += 1 print("\nSeverity distribution (Availability Score):") for score in sorted(score_distribution.keys()):
        count = score_distribution[score] percentage = count/len(severe_records)*100 print(f"Score {score}: {count} records ({percentage:.1f}%)") print("\nMost common severe keywords:")
        for keyword, count in keyword_counts.most_common(10):
            print(f"'{keyword}': {count} occurrences")
            return severe_records

def analyze_equipment_severity(data):
    """Analyze equipment severity based on availability scores""" equipment_stats = defaultdict(lambda: { 'scores': [], 'descriptions': set(), 'sections': set(), 'equipment_desc': '' }) for record in data:
    equipment_id = record['Num_equipement'] score = int(record['Disponibilté']) equipment_stats[equipment_id]['scores'].append(score) equipment_stats[equipment_id]['descriptions'].add(record['Description']) equipment_stats[equipment_id]['sections'].add(record['Section propriétaire']) if not equipment_stats[equipment_id]['equipment_desc']:
    equipment_stats[equipment_id]['equipment_desc'] = record['Description de l\'équipement'] equipment_analysis = [] for equipment_id, stats in equipment_stats.items():
    scores = stats['scores'] avg_score = sum(scores) / len(scores) max_score = max(scores) min_score = min(scores) occurrence_count = len(scores) import math severity_score = (avg_score * 0.4 + max_score * 0.3 + math.log(1 + occurrence_count) * 0.3) equipment_analysis.append({ 'Equipment_ID': equipment_id, 'Equipment_Description': stats['equipment_desc'][:50] + '...'
    if len(stats['equipment_desc']) > 50 else stats['equipment_desc'], 'Average_Score':
        round(avg_score, 2), 'Max_Score': max_score, 'Min_Score': min_score, 'Occurrence_Count': occurrence_count, 'Severity_Score': round(severity_score, 2), 'Sections': list(stats['sections']) }) equipment_analysis.sort(key=lambda x: x['Severity_Score'], reverse=True) print("\n=== EQUIPMENT SEVERITY ANALYSIS ===")
        print("\nTop 20 most critical equipment:") print(f"{'Equipment Description':<50} {'Avg Score':<10} {'Max Score':<10} {'Count':<8} {'Severity':<10}")
        print("-" * 90) for i, equipment in enumerate(equipment_analysis[:
        20]): print(f"{equipment['Equipment_Description']:<50} {equipment['Average_Score']:<10} " f"{equipment['Max_Score']:<10} {equipment['Occurrence_Count']:<8} {equipment['Severity_Score']:<10}") high_impact_equipment = [eq for eq in equipment_analysis if eq['Average_Score'] >= 4.0] high_impact_equipment.sort(key=lambda x:
        x['Average_Score'], reverse=True) print(f"\nEquipment with highest average availability impact (score >= 4.0):
        {len(high_impact_equipment)} items") print(f"{'Equipment Description':<50} {'Avg Score':<10} {'Count':<8}")
        print("-" * 70) for equipment in high_impact_equipment[:
        15]: print(f"{equipment['Equipment_Description']:<50} {equipment['Average_Score']:<10} {equipment['Occurrence_Count']:<8}")
        return equipment_analysis

def predict_next_anomalies(data, equipment_analysis):
    """Predict next anomalies based on patterns""" high_risk_equipment = [] for equipment in equipment_analysis:
    avg_occurrence = sum(eq['Occurrence_Count'] for eq in equipment_analysis) / len(equipment_analysis) risk_factors = 0 risk_reasons = [] if equipment['Severity_Score'] >= 3.5:
    risk_factors += 3 risk_reasons.append("High severity score") if equipment['Occurrence_Count'] > avg_occurrence:
    risk_factors += 2 risk_reasons.append("Frequent issues") if equipment['Average_Score'] >= 3.0:
    risk_factors += 2 risk_reasons.append("High impact issues") if equipment['Max_Score'] == 5:
    risk_factors += 1 risk_reasons.append("Critical issues recorded") if risk_factors >= 4:
    risk_level = "High" elif risk_factors >= 2:
    risk_level = "Medium" else:
    risk_level = "Low" high_risk_equipment.append({ 'Equipment_ID': equipment['Equipment_ID'], 'Equipment_Description': equipment['Equipment_Description'], 'Risk_Level': risk_level, 'Risk_Score': risk_factors, 'Risk_Reasons': risk_reasons, 'Severity_Score': equipment['Severity_Score'], 'Occurrence_Count': equipment['Occurrence_Count'] }) high_risk_equipment.sort(key=lambda x: x['Risk_Score'], reverse=True) print("\n=== NEXT ANOMALY PREDICTION ===")
    print(f"\nHigh-risk equipment for next anomalies (Top 20):
    ") print(f"{'Equipment Description':<50} {'Risk Level':<12} {'Risk Score':<10} {'Occurrences':<12}")
    print("-" * 86) for equipment in high_risk_equipment[:
    20]: print(f"{equipment['Equipment_Description']:<50} {equipment['Risk_Level']:<12} " f"{equipment['Risk_Score']:<10} {equipment['Occurrence_Count']:<12}")
    return high_risk_equipment

def generate_ml_features(data):
    """Generate features that could be used for machine learning""" print("\n=== MACHINE LEARNING FEATURES ===") word_frequency = Counter() for record in data:
    words = re.findall(r'\b\w+\b', record['Description'].lower()) word_frequency.update(words) print("Most common words in descriptions (potential features):") for word, count in word_frequency.most_common(20):
    if len(word) > 3:
        print(f"'{word}': {count} occurrences") from datetime
import datetime year_counts = Counter() month_counts = Counter()
for record in data:
    try:
        date = datetime.strptime(record['Date de détéction de l\'anomalie'], '%Y-%m-%d %H:%M:%S') year_counts[date.year] += 1 month_counts[date.month] += 1 except:
        continue print("\nTemporal patterns:")
        print("Issues by year:", dict(year_counts)) print("Issues by month:", dict(month_counts)) section_scores = defaultdict(list) for record in data:
        section_scores[record['Section propriétaire']].append(int(record['Disponibilté'])) section_avg_severity = {} for section, scores in section_scores.items():
        section_avg_severity[section] = sum(scores) / len(scores) print("\nSection average severity:")
        for section, avg_score in sorted(section_avg_severity.items(), key=lambda x:
            x[1], reverse=True)[:10]: print(f"{section}: {avg_score:.2f}")
def export_results(severe_records, equipment_analysis, high_risk_equipment):
    """Export results to CSV files""" with open('data/severe_descriptions_with_scores.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file) writer.writerow(['Description', 'Availability_Score', 'Equipment_Description', 'Section', 'Date', 'Keywords_Found']) for record in severe_records:
    writer.writerow([ record['Description'], record['Availability_Score'], record['Equipment_Description'], record['Section'], record['Date'], '; '.join(record['Found_Keywords']) ]) with open('data/equipment_severity_ranking.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file) writer.writerow(['Equipment_ID', 'Equipment_Description', 'Average_Score', 'Max_Score', 'Min_Score', 'Occurrence_Count', 'Severity_Score', 'Sections']) for equipment in equipment_analysis:
    writer.writerow([ equipment['Equipment_ID'], equipment['Equipment_Description'], equipment['Average_Score'], equipment['Max_Score'], equipment['Min_Score'], equipment['Occurrence_Count'], equipment['Severity_Score'], '; '.join(equipment['Sections']) ]) with open('data/next_anomaly_predictions.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file) writer.writerow(['Equipment_ID', 'Equipment_Description', 'Risk_Level', 'Risk_Score', 'Risk_Reasons', 'Severity_Score', 'Occurrence_Count']) for equipment in high_risk_equipment:
    writer.writerow([ equipment['Equipment_ID'], equipment['Equipment_Description'], equipment['Risk_Level'], equipment['Risk_Score'], '; '.join(equipment['Risk_Reasons']), equipment['Severity_Score'], equipment['Occurrence_Count'] ]) print("\n=== EXPORT COMPLETE ===")
    print("Files created:") print("data/- severe_descriptions_with_scores.csv")
    print("data/- equipment_severity_ranking.csv") print("data/- next_anomaly_predictions.csv")
def main():
    """Main analysis function""" print("Starting Availability Analysis (Simple Version)...") print("=" * 60)
    try:
        data = load_data() print(f"data/Loaded {len(data)} records from disponibilite.csv") severe_records = extract_severe_descriptions(data) equipment_analysis = analyze_equipment_severity(data) high_risk_equipment = predict_next_anomalies(data, equipment_analysis) generate_ml_features(data) export_results(severe_records, equipment_analysis, high_risk_equipment) print("\n" + "=" * 60)
        print("Analysis complete! Check the generated CSV files
        for detailed results.") print("\nSummary:
            ")
            print(f"- Found {len(severe_records)} severe issues out of {len(data)} total records") print(f"- Analyzed {len(equipment_analysis)} unique equipment items") print(f"- Identified {len([eq for eq in high_risk_equipment if eq['Risk_Level'] == 'High'])} high-risk equipment for monitoring") except Exception as e:
            print(f"Error during analysis: {e}") import traceback traceback.print_exc()
            if __name__ == "__main__":
                main()