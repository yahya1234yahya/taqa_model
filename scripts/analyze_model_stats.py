import pandas as pd
import numpy as np import pickle
from datetime
import datetime

def analyze_datasets():
    print(" ANALYZING ACTUAL MODEL DATA")
    print("="*50) try:
    availability_data = pd.read_csv('data/disponibilite.csv') reliability_data = pd.read_csv('data/fiabilite.csv') safety_data = pd.read_csv('data/process_safty.csv') print(f"\n DATASET SIZES:")
    print(f"Availability dataset: {len(availability_data):,} records") print(f"Reliability dataset: {len(reliability_data):,} records") print(f"Process Safety dataset: {len(safety_data):,} records") print(f"\n SCORE DISTRIBUTIONS (1-5 scale):") datasets = { 'Availability': (availability_data, 'Disponibilté'), 'Reliability': (reliability_data, 'Fiabilité Intégrité'), 'Process Safety': (safety_data, 'Process Safety') } for name, (data, col) in datasets.items():
    scores = data[col].dropna() print(f"\n{name}:")
    print(f" Mean: {scores.mean():.2f}") print(f" Std Dev: {scores.std():.2f}") print(f" Min: {scores.min()}") print(f" Max: {scores.max()}") print(f" Most Common: {scores.mode().iloc[0]}") print(f" Score 1: {(scores == 1).sum():,} ({(scores == 1).mean()*100:.1f}%)") print(f" Score 2: {(scores == 2).sum():,} ({(scores == 2).mean()*100:.1f}%)") print(f" Score 3: {(scores == 3).sum():,} ({(scores == 3).mean()*100:.1f}%)") print(f" Score 4: {(scores == 4).sum():,} ({(scores == 4).mean()*100:.1f}%)") print(f" Score 5: {(scores == 5).sum():,} ({(scores == 5).mean()*100:.1f}%)") print(f"\n TEXT ANALYSIS:")
    for name, (data, col) in datasets.items():
        descriptions = data['Description'].dropna() equipment_names = data['Description de l\'équipement'].dropna() print(f"\n{name}:")
        print(f" Avg Description Length: {descriptions.str.len().mean():.0f} chars") print(f" Avg Equipment Name Length: {equipment_names.str.len().mean():.0f} chars") print(f" Longest Description: {descriptions.str.len().max()} chars") print(f" Shortest Description: {descriptions.str.len().min()} chars") print(f"\n TEMPORAL ANALYSIS:")
        for name, (data, col) in datasets.items():
            dates = pd.to_datetime(data['Date de détéction de l\'anomalie']) print(f"\n{name}:")
            print(f" Date Range: {dates.min()} to {dates.max()}") print(f" Most Common Hour: {dates.dt.hour.mode().iloc[0]}:00") print(f" Most Common Day: {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][dates.dt.dayofweek.mode().iloc[0]]}") return True

            except Exception as e:
                print(f" Error analyzing datasets: {e}")
                return False

def analyze_models():
    print(f"\n MODEL ANALYSIS:")
    print("="*50) try:
    models = {} with open('models/availability_model.pkl', 'rb') as f:
    models['Availability'] = pickle.load(f) with open('models/fiability_model.pkl', 'rb') as f:
    models['Reliability'] = pickle.load(f) with open('models/process_safety_model.pkl', 'rb') as f:
    models['Process Safety'] = pickle.load(f) for name, model_dict in models.items():
    print(f"\n{name} Model:")
    print(f" Model Type: {type(model_dict['model']).__name__}") print(f" Features Count: {len(model_dict['feature_names'])}") print(f" Equipment Scores: {len(model_dict['equipment_scores'])} unique equipments") print(f" Word Scores: {len(model_dict['word_scores'])} keywords") model = model_dict['model'] if hasattr(model, 'n_estimators'):
    print(f" Estimators: {model.n_estimators}")
    if hasattr(model, 'max_depth'):
        print(f" Max Depth: {model.max_depth}")
        if hasattr(model, 'random_state'):
            print(f" Random State: {model.random_state}")
            return True

        except Exception as e:
            print(f" Error analyzing models: {e}")
            return False

def analyze_keywords():
    print(f"\n KEYWORD ANALYSIS:")
    print("="*50) try:
    files_to_check = [ 'data/severe_words_simple.csv', 'data/severe_words_fiability_simple.csv', 'data/severe_words_process_safety_simple.csv' ] for filename in files_to_check:
    try:
        keywords = pd.read_csv(filename) print(f"\n{filename}:")
        print(f" Total Keywords: {len(keywords)}") if 'Average_Score' in keywords.columns:
        scores = keywords['Average_Score'] print(f" Avg Keyword Score: {scores.mean():.2f}") print(f" High Impact Keywords (>3): {(scores > 3).sum()}") print(f" Critical Keywords (>4): {(scores > 4).sum()}") except FileNotFoundError:
        print(f" {filename}: File not found")
        return True

    except Exception as e:
        print(f" Error analyzing keywords: {e}")
        return False

def analyze_equipment():
    print(f"\n EQUIPMENT ANALYSIS:")
    print("="*50) try:
    equipment = pd.read_csv('data/equipment_simple.csv') print(f" Total Equipment Records: {len(equipment):,}") if 'Average_Score' in equipment.columns:
    scores = equipment['Average_Score'] print(f" Avg Equipment Score: {scores.mean():.2f}") print(f" Equipment Score Range: {scores.min():.1f} - {scores.max():.1f}") print(f" High Risk Equipment (>3): {(scores > 3).sum()}") if 'Section' in equipment.columns:
    sections = equipment['Section'].value_counts() print(f" Unique Sections: {len(sections)}") print(f" Most Active Section: {sections.index[0]} ({sections.iloc[0]} records)") return True

    except Exception as e:
        print(f" Error analyzing equipment: {e}")
        return False

def generate_summary_stats():
    print(f"\n SUMMARY STATISTICS FOR VISUALIZATION:")
    print("="*60) """)

def main():
    print(" COMPREHENSIVE MODEL STATISTICS ANALYSIS")
    print("="*60) print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") analyze_datasets() analyze_models() analyze_keywords() analyze_equipment() generate_summary_stats() print(f"\n Analysis Complete!")
    print("Use these numbers in your model statistics visualizations.") if __name__ == "__main__":
    main()