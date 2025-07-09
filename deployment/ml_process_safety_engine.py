import pandas as pd
import numpy as np
import re
from collections import defaultdict
import pickle

class ProcessSafetyPredictor:
    """
    Feature Engineering and Prediction Pipeline for Equipment Process Safety
    """
    
    def __init__(self):
        self.equipment_data = None
        self.severe_words_data = None
        self.word_scores = {}
        self.equipment_scores = {}
        self.model = None
        self.feature_names = []
        
    def load_historical_data(self):
        """Load the preprocessed equipment and severe words data for process safety"""
        
        print("Loading process safety historical data...")
        
        # Load equipment data
        self.equipment_data = pd.read_csv('equipment_process_safety_simple.csv')
        print(f"Loaded {len(self.equipment_data)} equipment records")
        
        # Load severe words data  
        self.severe_words_data = pd.read_csv('severe_words_process_safety_simple.csv')
        print(f"Loaded {len(self.severe_words_data)} severe words")
        
        # Create lookup dictionaries for fast access
        self.equipment_scores = dict(zip(
            self.equipment_data['Equipment_ID'], 
            self.equipment_data['Average_Process_Safety_Score']
        ))
        
        self.word_scores = dict(zip(
            self.severe_words_data['Word'], 
            self.severe_words_data['Average_Process_Safety_Score']
        ))
        
        print("Process safety historical data loaded successfully!")
        
    def extract_features(self, description, equipment_name, equipment_id):
        """
        Extract features from user input for process safety ML prediction
        
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
        
        # 1. Historical equipment average process safety score
        features['equipment_historical_avg'] = self.equipment_scores.get(equipment_id, 2.5)  # Default to middle score
        
        # 2. Equipment risk category (based on historical process safety score)
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
        features['is_safety_critical'] = 1 if any(word in eq_name_lower for word in ['safety', 'sécurité', 'protection', 'secours']) else 0
        
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
        
        # 6. Weighted severity score (considering word importance for process safety)
        safety_weights = {
            'explosion': 10, 'fire': 10, 'incendie': 10, 'toxique': 10,
            'safety': 8, 'sécurité': 8, 'danger': 8, 'dangereuse': 8,
            'urgent': 6, 'critique': 6, 'critical': 6, 'emergency': 6,
            'fuite importante': 5, 'major leak': 5, 'rupture': 5,
            'alarme': 3, 'alarm': 3, 'anormal': 3, 'pression': 2
        }
        
        weighted_score = 0
        total_weight = 0
        for word in found_words:
            weight = safety_weights.get(word, 1)
            score = self.word_scores[word]
            weighted_score += score * weight
            total_weight += weight
            
        features['weighted_safety_score'] = weighted_score / total_weight if total_weight > 0 else 2.5
        
        # 7. Safety-specific categories
        safety_critical_words = ['safety', 'sécurité', 'danger', 'explosion', 'fire', 'toxique', 'emergency']
        pressure_words = ['pression', 'pressure', 'surpression', 'overpressure', 'explosion', 'soupape']
        temperature_words = ['température', 'temp', 'chaud', 'surchauffe', 'refroidissement', 'échauffement']
        leak_words = ['fuite', 'étanchéité', 'percement', 'infiltration', 'leak']
        electrical_words = ['alarme', 'alarm', 'électrique', 'court-circuit', 'arc', 'décharge']
        mechanical_words = ['vibration', 'bruit', 'usure', 'blocage', 'casse', 'fracture']
        
        features['has_safety_critical_issue'] = 1 if any(word in desc_lower for word in safety_critical_words) else 0
        features['has_pressure_issue'] = 1 if any(word in desc_lower for word in pressure_words) else 0
        features['has_temperature_issue'] = 1 if any(word in desc_lower for word in temperature_words) else 0
        features['has_leakage_issue'] = 1 if any(word in desc_lower for word in leak_words) else 0
        features['has_electrical_issue'] = 1 if any(word in desc_lower for word in electrical_words) else 0
        features['has_mechanical_issue'] = 1 if any(word in desc_lower for word in mechanical_words) else 0
        
        # 8. Text characteristics
        features['description_length'] = len(description)
        features['description_word_count'] = len(description.split())
        
        # 9. Emergency and urgency indicators
        emergency_words = ['urgent', 'urgence', 'emergency', 'critique', 'arrêt d\'urgence', 'evacuation']
        features['emergency_score'] = sum(1 for word in emergency_words if word in desc_lower)
        
        # 10. Process safety hazard levels
        hazard_level_1 = ['explosion', 'fire', 'toxique', 'poison', 'asphyxie']  # Catastrophic
        hazard_level_2 = ['fuite importante', 'surpression', 'surchauffe', 'court-circuit']  # Major
        hazard_level_3 = ['fuite', 'alarme', 'vibration', 'décharge']  # Moderate
        
        features['catastrophic_hazard'] = 1 if any(word in desc_lower for word in hazard_level_1) else 0
        features['major_hazard'] = 1 if any(word in desc_lower for word in hazard_level_2) else 0
        features['moderate_hazard'] = 1 if any(word in desc_lower for word in hazard_level_3) else 0
        
        # === INTERACTION FEATURES ===
        
        # 11. Equipment-safety interaction
        features['equipment_safety_interaction'] = features['equipment_historical_avg'] * features['severe_words_avg_score']
        
        # 12. Critical safety amplifier
        if (features['equipment_risk_level'] >= 3 and features['severe_words_count'] > 2) or features['catastrophic_hazard']:
            features['critical_safety_amplifier'] = 1
        else:
            features['critical_safety_amplifier'] = 0
            
        # 13. Combined safety risk score
        features['combined_safety_risk'] = (
            (5 - features['equipment_historical_avg']) * 0.3 +  # Equipment risk (inverted)
            (5 - features['severe_words_avg_score']) * 0.3 +    # Description risk (inverted)
            features['severe_words_count'] * 0.2 +              # Severity count
            features['emergency_score'] * 0.1 +                 # Emergency indicators
            features['catastrophic_hazard'] * 0.1               # Catastrophic hazard bonus
        )
        
        return features
    
    def prepare_training_data(self, original_data_file='process_safty.csv'):
        """
        Prepare training data using historical process safety records
        """
        
        print("Preparing process safety training data...")
        
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
            y.append(row['Process Safety'])
            
        # Store feature names for later use
        sample_features = self.extract_features("test", "test", "test")
        self.feature_names = list(sample_features.keys())
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"Process safety training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        
        return X, y
    
    def train_model(self, X, y):
        """
        Train a Random Forest model for process safety prediction
        """
        
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        
        print("Training process safety model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"Process safety model trained successfully!")
        print(f"Test MAE: {mae:.3f}")
        print(f"Test RMSE: {rmse:.3f}")
        
        # Feature importance
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features for Process Safety:")
        print(feature_importance.head(10))
        
        return self.model
    
    def predict_process_safety(self, description, equipment_name, equipment_id):
        """
        Predict process safety for new input
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
            'avg_safety_score': round(features['severe_words_avg_score'], 2),
            'combined_safety_risk': round(features['combined_safety_risk'], 2),
            'catastrophic_hazard': features['catastrophic_hazard'],
            'safety_critical_equipment': features['is_safety_critical'],
            'predicted_process_safety': round(prediction, 2)
        }
        
        return prediction, features, feature_explanation
    
    def save_model(self, filepath='process_safety_model.pkl'):
        """Save the trained process safety model and data"""
        
        model_data = {
            'model': self.model,
            'equipment_scores': self.equipment_scores,
            'word_scores': self.word_scores,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Process safety model saved to {filepath}")
    
    def load_model(self, filepath='process_safety_model.pkl'):
        """Load a pre-trained process safety model"""
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.equipment_scores = model_data['equipment_scores']
        self.word_scores = model_data['word_scores']
        self.feature_names = model_data['feature_names']
        
        print(f"Process safety model loaded from {filepath}")

def main():
    """
    Example usage of the ProcessSafetyPredictor
    """
    
    print("=== PROCESS SAFETY PREDICTION SYSTEM ===")
    print()
    
    # Initialize predictor
    predictor = ProcessSafetyPredictor()
    
    # Load historical data
    predictor.load_historical_data()
    
    # Prepare training data
    X, y = predictor.prepare_training_data()
    
    # Train model
    predictor.train_model(X, y)
    
    # Save model
    predictor.save_model()
    
    print("\n" + "="*60)
    print("TESTING PROCESS SAFETY PREDICTIONS")
    print("="*60)
    
    # Test predictions
    test_cases = [
        {
            'description': 'Explosion risque détectée avec fuite de gaz et alarme sécurité',
            'equipment_name': 'SAFETY VALVE SYSTEM',
            'equipment_id': 'f9dd64bd-99ea-488d-801a-c499690bfa17'
        },
        {
            'description': 'Maintenance préventive normale, contrôle de routine',
            'equipment_name': 'MILL MAINTENANCE HOIST',
            'equipment_id': '1506a5da-0145-49a3-9117-1cfa8f1e8811'
        },
        {
            'description': 'Alarme critique surchauffe moteur avec arrêt d\'urgence immédiat',
            'equipment_name': 'MOTEUR POMPE HYDRAULIQUE',
            'equipment_id': 'test-motor-001'
        },
        {
            'description': 'Fuite importante vapeur toxique avec évacuation personnel',
            'equipment_name': 'STEAM SYSTEM',
            'equipment_id': 'test-steam-001'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Process Safety Test Case {i} ---")
        print(f"Equipment: {test['equipment_name']}")
        print(f"Description: {test['description']}")
        
        prediction, features, explanation = predictor.predict_process_safety(
            test['description'], 
            test['equipment_name'], 
            test['equipment_id']
        )
        
        print(f"\nPredicted Process Safety: {prediction:.2f}/5")
        print(f"Safety Risk Analysis:")
        print(f"  - Equipment Risk Level: {explanation['equipment_risk']}/4")
        print(f"  - Severe Words Found: {explanation['severe_words_found']}")
        print(f"  - Average Safety Score: {explanation['avg_safety_score']}")
        print(f"  - Combined Safety Risk: {explanation['combined_safety_risk']}")
        print(f"  - Catastrophic Hazard: {'YES' if explanation['catastrophic_hazard'] else 'NO'}")
        print(f"  - Safety Critical Equipment: {'YES' if explanation['safety_critical_equipment'] else 'NO'}")
        
        # Safety interpretation
        if prediction >= 4:
            safety_level = "SAFE"
            color = "🟢"
        elif prediction >= 3:
            safety_level = "MODERATE RISK"
            color = "🟡"
        elif prediction >= 2:
            safety_level = "HIGH RISK"
            color = "🟠"
        else:
            safety_level = "CRITICAL RISK"
            color = "🔴"
            
        print(f"  - Safety Level: {color} {safety_level}")
        
        # Safety recommendations
        if explanation['catastrophic_hazard']:
            print(f"  ⚠️  CATASTROPHIC HAZARD DETECTED - IMMEDIATE ACTION REQUIRED!")
        elif prediction < 2:
            print(f"  🚨 STOP OPERATIONS - CRITICAL SAFETY RISK")
        elif prediction < 3:
            print(f"  ⚠️  HIGH PRIORITY SAFETY REVIEW NEEDED")

if __name__ == "__main__":
    main() 