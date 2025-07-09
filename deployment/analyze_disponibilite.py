import pandas as pd
import numpy as np
import re
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def load_and_analyze_data():
    """Load and perform initial analysis of the data"""
    # Load the CSV file
    df = pd.read_csv('disponibilite.csv')
    
    print("=== DATA OVERVIEW ===")
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Date range: {df['Date de détéction de l\'anomalie'].min()} to {df['Date de détéction de l\'anomalie'].max()}")
    print(f"Availability scores range: {df['Disponibilté'].min()} to {df['Disponibilté'].max()}")
    print(f"Unique equipment: {df['Num_equipement'].nunique()}")
    print(f"Unique systems: {df['Systeme'].nunique()}")
    
    return df

def extract_severe_descriptions(df):
    """Extract descriptions containing severe-related keywords and their availability scores"""
    
    # Keywords that indicate severity (in French and English)
    severe_keywords = [
        'sévère', 'severe', 'grave', 'important', 'importante', 'critique', 'critical',
        'urgent', 'danger', 'fuite importante', 'défaillance', 'panne', 'arrêt',
        'bruit anormal', 'vibration', 'surchauffe', 'échauffement', 'percement',
        'fissure', 'casse', 'détérioration', 'aggravation'
    ]
    
    # Create a pattern to match any of these keywords
    pattern = '|'.join(severe_keywords)
    
    # Find records with severe descriptions
    severe_mask = df['Description'].str.contains(pattern, case=False, na=False)
    severe_records = df[severe_mask].copy()
    
    print("\n=== SEVERE DESCRIPTIONS ANALYSIS ===")
    print(f"Total severe records found: {len(severe_records)}")
    
    # Group by availability score
    severity_distribution = severe_records['Disponibilté'].value_counts().sort_index()
    print("\nSeverity distribution (Availability Score):")
    for score, count in severity_distribution.items():
        print(f"Score {score}: {count} records ({count/len(severe_records)*100:.1f}%)")
    
    # Most common severe issues
    print("\nMost common severe issues:")
    severe_descriptions = severe_records['Description'].str.lower()
    for keyword in severe_keywords:
        count = severe_descriptions.str.contains(keyword, na=False).sum()
        if count > 0:
            print(f"'{keyword}': {count} occurrences")
    
    return severe_records

def analyze_equipment_severity(df):
    """Analyze equipment severity based on availability scores"""
    
    # Calculate equipment severity metrics
    equipment_stats = df.groupby(['Num_equipement', 'Description de l\'équipement']).agg({
        'Disponibilté': ['mean', 'max', 'min', 'count', 'std'],
        'Description': 'count'
    }).reset_index()
    
    # Flatten column names
    equipment_stats.columns = [
        'Equipment_ID', 'Equipment_Description', 
        'Avg_Availability_Score', 'Max_Availability_Score', 
        'Min_Availability_Score', 'Occurrence_Count', 'Std_Availability_Score',
        'Total_Issues'
    ]
    
    # Fill NaN in std with 0 (for equipment with only one record)
    equipment_stats['Std_Availability_Score'] = equipment_stats['Std_Availability_Score'].fillna(0)
    
    # Calculate severity score (combination of average score, max score, and frequency)
    equipment_stats['Severity_Score'] = (
        equipment_stats['Avg_Availability_Score'] * 0.4 +
        equipment_stats['Max_Availability_Score'] * 0.3 +
        np.log1p(equipment_stats['Occurrence_Count']) * 0.3
    )
    
    # Sort by severity score
    equipment_stats = equipment_stats.sort_values('Severity_Score', ascending=False)
    
    print("\n=== EQUIPMENT SEVERITY ANALYSIS ===")
    print("\nTop 10 most critical equipment:")
    print(equipment_stats[['Equipment_Description', 'Avg_Availability_Score', 
                          'Max_Availability_Score', 'Occurrence_Count', 'Severity_Score']].head(10))
    
    # Equipment with highest average availability impact
    print("\nEquipment with highest average availability impact:")
    high_impact = equipment_stats[equipment_stats['Avg_Availability_Score'] >= 4].head(10)
    print(high_impact[['Equipment_Description', 'Avg_Availability_Score', 'Occurrence_Count']])
    
    return equipment_stats

def prepare_ml_data(df):
    """Prepare data for machine learning to predict anomaly severity"""
    
    # Create features for ML
    ml_df = df.copy()
    
    # Convert date to datetime and extract features
    ml_df['Date'] = pd.to_datetime(ml_df['Date de détéction de l\'anomalie'])
    ml_df['Year'] = ml_df['Date'].dt.year
    ml_df['Month'] = ml_df['Date'].dt.month
    ml_df['DayOfWeek'] = ml_df['Date'].dt.dayofweek
    ml_df['DayOfYear'] = ml_df['Date'].dt.dayofyear
    
    # Text features from description
    # Clean and preprocess text
    ml_df['Description_Clean'] = ml_df['Description'].str.lower().str.replace('[^\w\s]', '', regex=True)
    
    # Create TF-IDF features from descriptions
    tfidf = TfidfVectorizer(max_features=100, stop_words=None, ngram_range=(1, 2))
    tfidf_features = tfidf.fit_transform(ml_df['Description_Clean'].fillna(''))
    
    # Convert to DataFrame
    tfidf_df = pd.DataFrame(tfidf_features.toarray(), 
                           columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])])
    
    # Equipment frequency (how often this equipment has issues)
    equipment_counts = ml_df['Num_equipement'].value_counts()
    ml_df['Equipment_Frequency'] = ml_df['Num_equipement'].map(equipment_counts)
    
    # System frequency
    system_counts = ml_df['Systeme'].value_counts()
    ml_df['System_Frequency'] = ml_df['Systeme'].map(system_counts)
    
    # Historical severity for this equipment
    ml_df = ml_df.sort_values('Date')
    ml_df['Historical_Avg_Severity'] = ml_df.groupby('Num_equipement')['Disponibilté'].expanding().mean().reset_index(0, drop=True)
    
    # Time since last issue for this equipment
    ml_df['Days_Since_Last_Issue'] = ml_df.groupby('Num_equipement')['Date'].diff().dt.days.fillna(0)
    
    # Combine all features
    feature_columns = ['Year', 'Month', 'DayOfWeek', 'DayOfYear', 
                      'Equipment_Frequency', 'System_Frequency', 
                      'Historical_Avg_Severity', 'Days_Since_Last_Issue']
    
    X = pd.concat([ml_df[feature_columns].reset_index(drop=True), tfidf_df], axis=1)
    y = ml_df['Disponibilté'].values
    
    # Fill missing values
    X = X.fillna(0)
    
    print("\n=== MACHINE LEARNING DATA PREPARATION ===")
    print(f"Feature matrix shape: {X.shape}")
    print(f"Target variable distribution:")
    print(pd.Series(y).value_counts().sort_index())
    
    return X, y, tfidf, ml_df

def train_anomaly_prediction_model(X, y):
    """Train a model to predict anomaly severity"""
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf_model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = rf_model.predict(X_test_scaled)
    
    print("\n=== MODEL PERFORMANCE ===")
    print("Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10))
    
    return rf_model, scaler, feature_importance

def predict_next_anomaly(df, model, scaler, tfidf):
    """Predict next anomaly based on recent patterns"""
    
    # Find equipment with recent issues
    recent_date = df['Date de détéction de l\'anomalie'].max()
    recent_df = df[df['Date de détéction de l\'anomalie'] >= recent_date].copy()
    
    # Get equipment that had issues recently
    recent_equipment = recent_df['Num_equipement'].unique()
    
    print("\n=== NEXT ANOMALY PREDICTION ===")
    print(f"Analyzing {len(recent_equipment)} equipment with recent issues")
    
    # For demonstration, predict for equipment with high frequency of issues
    equipment_counts = df['Num_equipement'].value_counts()
    high_risk_equipment = equipment_counts.head(10).index
    
    predictions = []
    for equipment_id in high_risk_equipment:
        equipment_data = df[df['Num_equipement'] == equipment_id].iloc[-1]
        equipment_desc = equipment_data['Description de l\'équipement']
        last_severity = equipment_data['Disponibilté']
        
        predictions.append({
            'Equipment_ID': equipment_id,
            'Equipment_Description': equipment_desc,
            'Last_Severity': last_severity,
            'Risk_Level': 'High' if last_severity >= 4 else 'Medium' if last_severity >= 2 else 'Low'
        })
    
    prediction_df = pd.DataFrame(predictions)
    print("\nHigh-risk equipment for next anomalies:")
    print(prediction_df)
    
    return prediction_df

def create_visualizations(df, equipment_stats, severe_records):
    """Create visualizations for the analysis"""
    
    plt.figure(figsize=(15, 12))
    
    # 1. Availability score distribution
    plt.subplot(2, 3, 1)
    df['Disponibilté'].value_counts().sort_index().plot(kind='bar')
    plt.title('Distribution of Availability Scores')
    plt.xlabel('Availability Score')
    plt.ylabel('Count')
    
    # 2. Severe vs Non-severe issues
    plt.subplot(2, 3, 2)
    severe_count = len(severe_records)
    non_severe_count = len(df) - severe_count
    plt.pie([severe_count, non_severe_count], labels=['Severe', 'Non-severe'], autopct='%1.1f%%')
    plt.title('Severe vs Non-severe Issues')
    
    # 3. Timeline of issues
    plt.subplot(2, 3, 3)
    df['Date'] = pd.to_datetime(df['Date de détéction de l\'anomalie'])
    monthly_issues = df.groupby(df['Date'].dt.to_period('M')).size()
    monthly_issues.plot()
    plt.title('Issues Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Issues')
    plt.xticks(rotation=45)
    
    # 4. Top 10 equipment by severity score
    plt.subplot(2, 3, 4)
    top_equipment = equipment_stats.head(10)
    plt.barh(range(len(top_equipment)), top_equipment['Severity_Score'])
    plt.yticks(range(len(top_equipment)), [desc[:30] + '...' if len(desc) > 30 else desc 
                                          for desc in top_equipment['Equipment_Description']])
    plt.title('Top 10 Equipment by Severity Score')
    plt.xlabel('Severity Score')
    
    # 5. Section vs Availability Impact
    plt.subplot(2, 3, 5)
    section_impact = df.groupby('Section propriétaire')['Disponibilté'].mean().sort_values(ascending=False)
    section_impact.head(10).plot(kind='bar')
    plt.title('Average Availability Impact by Section')
    plt.xlabel('Section')
    plt.ylabel('Average Availability Score')
    plt.xticks(rotation=45)
    
    # 6. Equipment frequency vs severity
    plt.subplot(2, 3, 6)
    plt.scatter(equipment_stats['Occurrence_Count'], equipment_stats['Avg_Availability_Score'], alpha=0.6)
    plt.xlabel('Number of Issues')
    plt.ylabel('Average Availability Score')
    plt.title('Equipment Frequency vs Severity')
    
    plt.tight_layout()
    plt.savefig('availability_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def export_results(severe_records, equipment_stats, prediction_df):
    """Export results to CSV files"""
    
    # Export severe descriptions with availability scores
    severe_export = severe_records[['Description', 'Disponibilté', 'Description de l\'équipement', 
                                  'Section propriétaire', 'Date de détéction de l\'anomalie']].copy()
    severe_export.to_csv('severe_descriptions_with_scores.csv', index=False)
    
    # Export equipment severity ranking
    equipment_stats.to_csv('equipment_severity_ranking.csv', index=False)
    
    # Export predictions
    prediction_df.to_csv('next_anomaly_predictions.csv', index=False)
    
    print("\n=== EXPORT COMPLETE ===")
    print("Files created:")
    print("- severe_descriptions_with_scores.csv")
    print("- equipment_severity_ranking.csv") 
    print("- next_anomaly_predictions.csv")
    print("- availability_analysis.png")

def main():
    """Main analysis function"""
    
    print("Starting Availability Analysis...")
    
    # Load and analyze data
    df = load_and_analyze_data()
    
    # Extract severe descriptions
    severe_records = extract_severe_descriptions(df)
    
    # Analyze equipment severity
    equipment_stats = analyze_equipment_severity(df)
    
    # Prepare ML data
    X, y, tfidf, ml_df = prepare_ml_data(df)
    
    # Train model
    model, scaler, feature_importance = train_anomaly_prediction_model(X, y)
    
    # Predict next anomalies
    prediction_df = predict_next_anomaly(ml_df, model, scaler, tfidf)
    
    # Create visualizations
    create_visualizations(df, equipment_stats, severe_records)
    
    # Export results
    export_results(severe_records, equipment_stats, prediction_df)
    
    print("\nAnalysis complete! Check the generated files for detailed results.")

if __name__ == "__main__":
    main() 