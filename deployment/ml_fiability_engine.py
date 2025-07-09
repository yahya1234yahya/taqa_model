import pandas as pd
import numpy as np
import re
from collections import defaultdict
import pickle

class FiabilityPredictor:
    """
    Feature Engineering and Prediction Pipeline for Equipment Fiability
    """
    
    def __init__(self):
        self.equipment_data = None
        self.severe_words_data = None
        self.word_scores = {}
        self.equipment_scores = {}
        self.model = None
        self.feature_names = []
        
    def load_historical_data(self):
        """Load the preprocessed equipment and severe words data for fiability"""
        
        print("Loading fiability historical data...")
        
        # Load equipment data
        self.equipment_data = pd.read_csv('equipment_fiability_simple.csv')
        print(f"Loaded {len(self.equipment_data)} equipment records")
        
        # Load severe words data  
        self.severe_words_data = pd.read_csv('severe_words_fiability_simple.csv')
        print(f"Loaded {len(self.severe_words_data)} severe words")
        
        # Create lookup dictionaries for fast access
        self.equipment_scores = dict(zip(
            self.equipment_data['Equipment_ID'], 
            self.equipment_data['Average_Fiability_Score']
        ))
        
        self.word_scores = dict(zip(
            self.severe_words_data['Word'], 
            self.severe_words_data['Average_Fiability_Score']
        ))
        
        print("Fiability historical data loaded successfully!")
        
    def extract_features(self, description, equipment_name, equipment_id):
        """
        Extract features from user input for fiability ML prediction
        
        Args:
            description (str): Anomaly description
            equipment_name (str): Equipment name/description  
            equipment_id (str): Equipment unique identifier
            
        Returns:
            dict: Dictionary of features for ML model
        """
        
        features = {}
        
        # Handle missing/NaN values
        if pd.isna(equipment_id) or equipment_id is None:
            equipment_id = ""
        equipment_id = str(equipment_id)
        
        if pd.isna(equipment_name) or equipment_name is None:
            equipment_name = ""
        equipment_name = str(equipment_name)
        
        if pd.isna(description) or description is None:
            description = ""
        description = str(description)
        
        # === EQUIPMENT-BASED FEATURES ===
        
        # 1. Historical equipment average fiability score
        features['equipment_historical_avg'] = self.equipment_scores.get(equipment_id, 2.5)  # Default to middle score
        
        # 2. Equipment risk category (based on historical fiability score)
        eq_score = features['equipment_historical_avg']
        if eq_score >= 4.0:
            features['equipment_risk_level'] = 1  # Low risk
        elif eq_score >= 3.0:
            features['equipment_risk_level'] = 2  # Medium risk  
        elif eq_score >= 2.0:
            features['equipment_risk_level'] = 3  # High risk
        else:
            features['equipment_risk_level'] = 4  # Critical risk
            
        # 3. Equipment type indicators (from equipment name)
        eq_name_lower = equipment_name.lower()
        features['is_turbine'] = 1 if 'turbine' in eq_name_lower else 0
        features['is_pump'] = 1 if any(word in eq_name_lower for word in ['pompe', 'pump']) else 0
        features['is_motor'] = 1 if any(word in eq_name_lower for word in ['moteur', 'motor']) else 0
        features['is_valve'] = 1 if any(word in eq_name_lower for word in ['vanne', 'valve', 'soupape']) else 0
        features['is_sensor'] = 1 if any(word in eq_name_lower for word in ['capteur', 'sensor', 'transmetteur']) else 0
        features['is_electrical'] = 1 if any(word in eq_name_lower for word in ['électrique', 'electrical', 'disjoncteur']) else 0
        
        # === DESCRIPTION-BASED FEATURES ===
        
        desc_lower = description.lower()
        
        # 4. Severe words analysis
        found_words = []
        word_scores_found = []
        
        for word, score in self.word_scores.items():
            if word in desc_lower:
                found_words.append(word)
                word_scores_found.append(score)
        
        # 5. Severe words count and scoring
        features['severe_words_count'] = len(found_words)
        features['severe_words_avg_score'] = np.mean(word_scores_found) if word_scores_found else 2.5
        features['severe_words_min_score'] = min(word_scores_found) if word_scores_found else 2.5
        features['severe_words_max_score'] = max(word_scores_found) if word_scores_found else 2.5
        
        # 6. Weighted severity score (considering word importance for fiability)
        severity_weights = {
            'panne': 5, 'failure': 5, 'breakdown': 5,
            'urgent': 4, 'critique': 4, 'critical': 4,
            'surchauffe': 3, 'vibration': 3, 'fuite': 3,
            'alarme': 2, 'alarm': 2, 'anormal': 2
        }
        
        weighted_score = 0
        total_weight = 0
        for word in found_words:
            weight = severity_weights.get(word, 1)
            score = self.word_scores[word]
            weighted_score += score * weight
            total_weight += weight
            
        features['weighted_severity_score'] = weighted_score / total_weight if total_weight > 0 else 2.5
        
        # 7. Severity categories
        temp_words = ['température', 'temp', 'chaud', 'surchauffe', 'refroidissement', 'échauffement']
        mech_words = ['vibration', 'bruit', 'usure', 'blocage', 'oscillation']
        elec_words = ['alarme', 'alarm', 'électrique', 'court-circuit', 'arc']
        leak_words = ['fuite', 'étanchéité', 'percement', 'infiltration']
        
        features['has_temperature_issue'] = 1 if any(word in desc_lower for word in temp_words) else 0
        features['has_mechanical_issue'] = 1 if any(word in desc_lower for word in mech_words) else 0
        features['has_electrical_issue'] = 1 if any(word in desc_lower for word in elec_words) else 0
        features['has_leakage_issue'] = 1 if any(word in desc_lower for word in leak_words) else 0
        
        # 8. Text characteristics
        features['description_length'] = len(description)
        features['description_word_count'] = len(description.split())
        
        # 9. Urgency indicators
        urgency_words = ['urgent', 'urgence', 'emergency', 'critique', 'arrêt']
        features['urgency_score'] = sum(1 for word in urgency_words if word in desc_lower)
        
        # === INTERACTION FEATURES ===
        
        # 10. Equipment-severity interaction
        features['equipment_severity_interaction'] = features['equipment_historical_avg'] * features['severe_words_avg_score']
        
        # 11. Risk amplification factor
        if features['equipment_risk_level'] >= 3 and features['severe_words_count'] > 2:
            features['high_risk_amplifier'] = 1
        else:
            features['high_risk_amplifier'] = 0
            
        # 12. Combined risk score
        features['combined_risk_score'] = (
            (5 - features['equipment_historical_avg']) * 0.4 +  # Equipment risk (inverted)
            (5 - features['severe_words_avg_score']) * 0.4 +    # Description risk (inverted)
            features['severe_words_count'] * 0.2                # Severity count
        )
        
        return features
    
    def prepare_training_data(self, original_data_file='fiabilite.csv'):
        """
        Prepare training data using historical fiability records
        """
        
        print("Preparing fiability training data...")
        
        # Load original data
        df = pd.read_csv(original_data_file)
        
        # Create feature matrix
        X = []
        y = []
        
        for _, row in df.iterrows():
            features = self.extract_features(
                description=row['Description'],
                equipment_name=row['Description de l\'équipement'],
                equipment_id=row['Num_equipement']
            )
            
            X.append(list(features.values()))
            y.append(row['Fiabilité Intégrité'])
            
        # Store feature names for later use
        sample_features = self.extract_features("test", "test", "test")
        self.feature_names = list(sample_features.keys())
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"Fiability training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        
        return X, y
    
    def train_model(self, X, y):
        """
        Train a Random Forest model for fiability prediction
        """
        
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        
        print("Training fiability model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"Fiability model trained successfully!")
        print(f"Test MAE: {mae:.3f}")
        print(f"Test RMSE: {rmse:.3f}")
        
        # Feature importance
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features for Fiability:")
        print(feature_importance.head(10))
        
        return self.model
    
    def predict_fiability(self, description, equipment_name, equipment_id):
        """
        Predict fiability for new input
        """
        
        if self.model is None:
            raise ValueError("Model not trained yet! Call train_model() first.")
        
        # Extract features
        features = self.extract_features(description, equipment_name, equipment_id)
        
        # Convert to array
        X = np.array([list(features.values())])
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Ensure prediction is within valid range (1-5)
        prediction = max(1, min(5, prediction))
        
        # Get feature explanation
        feature_explanation = {
            'equipment_risk': features['equipment_risk_level'],
            'severe_words_found': features['severe_words_count'],
            'avg_severity_score': round(features['severe_words_avg_score'], 2),
            'combined_risk': round(features['combined_risk_score'], 2),
            'predicted_fiability': round(prediction, 2)
        }
        
        return prediction, features, feature_explanation
    
    def save_model(self, filepath='fiability_model.pkl'):
        """Save the trained fiability model and data"""
        
        model_data = {
            'model': self.model,
            'equipment_scores': self.equipment_scores,
            'word_scores': self.word_scores,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Fiability model saved to {filepath}")
    
    def load_model(self, filepath='fiability_model.pkl'):
        """Load a pre-trained fiability model"""
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.equipment_scores = model_data['equipment_scores']
        self.word_scores = model_data['word_scores']
        self.feature_names = model_data['feature_names']
        
        print(f"Fiability model loaded from {filepath}")

def main():
    """
    Example usage of the FiabilityPredictor
    """
    
    print("=== FIABILITY PREDICTION SYSTEM ===")
    print()
    
    # Initialize predictor
    predictor = FiabilityPredictor()
    
    # Load historical data
    predictor.load_historical_data()
    
    # Prepare training data
    X, y = predictor.prepare_training_data()
    
    # Train model
    predictor.train_model(X, y)
    
    # Save model
    predictor.save_model()
    
    print("\n" + "="*60)
    print("TESTING FIABILITY PREDICTIONS")
    print("="*60)
    
    # Test predictions
    test_cases = [
        {
            'description': 'Vibration anormale détectée avec surchauffe du moteur et fuite d\'huile',
            'equipment_name': 'MOTEUR VENTILATEUR DE REFROIDISSEMENT',
            'equipment_id': 'ab035cf9-a239-48d8-9c75-cd09534f3a3a'
        },
        {
            'description': 'Contrôle de routine, maintenance préventive normale',
            'equipment_name': 'CAPTEUR DE VIBRATION',
            'equipment_id': '0bcba8ab-3b66-42ad-be29-e221a1e3e36a'
        },
        {
            'description': 'Alarme critique, défaillance électrique avec arrêt d\'urgence',
            'equipment_name': 'MOTOPOMPE',
            'equipment_id': '6bdbbc91-9134-4cd6-aa4b-782df8042214'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Fiability Test Case {i} ---")
        print(f"Equipment: {test['equipment_name']}")
        print(f"Description: {test['description']}")
        
        prediction, features, explanation = predictor.predict_fiability(
            test['description'], 
            test['equipment_name'], 
            test['equipment_id']
        )
        
        print(f"\nPredicted Fiability: {prediction:.2f}/5")
        print(f"Risk Analysis:")
        print(f"  - Equipment Risk Level: {explanation['equipment_risk']}/4")
        print(f"  - Severe Words Found: {explanation['severe_words_found']}")
        print(f"  - Average Severity Score: {explanation['avg_severity_score']}")
        print(f"  - Combined Risk Score: {explanation['combined_risk']}")
        
        # Risk interpretation
        if prediction >= 4:
            risk_level = "LOW RISK"
        elif prediction >= 3:
            risk_level = "MEDIUM RISK"
        elif prediction >= 2:
            risk_level = "HIGH RISK"
        else:
            risk_level = "CRITICAL RISK"
            
        print(f"  - Risk Level: {risk_level}")

if __name__ == "__main__":
    main() 