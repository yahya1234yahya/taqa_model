import pandas as pd
import numpy as np
import re
from collections import defaultdict
import pickle

class AvailabilityPredictor:
    """Availability prediction system using equipment history and text analysis"""

    def __init__(self):
        self.equipment_data = None
        self.severe_words_data = None
        self.word_scores = {}
        self.equipment_scores = {}
        self.model = None
        self.feature_names = []

    def load_historical_data(self):
        """Load the preprocessed equipment and severe words data"""
        print("Loading historical data...")
        self.equipment_data = pd.read_csv('data/equipment_simple.csv')
        print(f"Loaded {len(self.equipment_data)} equipment records")
        
        self.severe_words_data = pd.read_csv('data/severe_words_simple.csv')
        print(f"Loaded {len(self.severe_words_data)} severe words")
        
        self.equipment_scores = dict(zip(
            self.equipment_data['Equipment_ID'],
            self.equipment_data['Average_Score']
        ))
        
        self.word_scores = dict(zip(
            self.severe_words_data['Word'],
            self.severe_words_data['Average_Score']
        ))
        
        print("Historical data loaded successfully!")

    def extract_features(self, description, equipment_name, equipment_id):
        """Extract features from equipment description and metadata"""
        features = {}
        
        # Equipment historical analysis
        if pd.isna(equipment_id) or equipment_id is None:
            equipment_id = ""
        equipment_id = str(equipment_id)
        
        features['equipment_historical_avg'] = self.equipment_scores.get(equipment_id, 2.5)
        
        eq_score = features['equipment_historical_avg']
        if eq_score >= 4.0:
            features['equipment_risk_level'] = 1
        elif eq_score >= 3.0:
            features['equipment_risk_level'] = 2
        elif eq_score >= 2.0:
            features['equipment_risk_level'] = 3
        else:
        else:
            features['equipment_risk_level'] = 4
        
        # Equipment type analysis
        if pd.isna(equipment_name) or equipment_name is None:
            equipment_name = ""
        equipment_name = str(equipment_name)
        eq_name_lower = equipment_name.lower()
        
        features['is_turbine'] = 1 if 'turbine' in eq_name_lower else 0
        features['is_pump'] = 1 if any(word in eq_name_lower for word in ['pompe', 'pump']) else 0
        features['is_motor'] = 1 if any(word in eq_name_lower for word in ['moteur', 'motor']) else 0
        features['is_valve'] = 1 if any(word in eq_name_lower for word in ['vanne', 'valve', 'soupape']) else 0
        features['is_sensor'] = 1 if any(word in eq_name_lower for word in ['capteur', 'sensor', 'transmetteur']) else 0
        features['is_electrical'] = 1 if any(word in eq_name_lower for word in ['électrique', 'electrical', 'disjoncteur']) else 0
        
        # Description analysis
        if pd.isna(description) or description is None:
            description = ""
        description = str(description)
        desc_lower = description.lower()
        
        # Severe words analysis
        found_words = []
        word_scores_found = []
        for word, score in self.word_scores.items():
            if word in desc_lower:
                found_words.append(word)
                word_scores_found.append(score)
        
        features['severe_words_count'] = len(found_words)
        features['severe_words_avg_score'] = np.mean(word_scores_found) if word_scores_found else 2.5
        features['severe_words_min_score'] = min(word_scores_found) if word_scores_found else 2.5
        features['severe_words_max_score'] = max(word_scores_found) if word_scores_found else 2.5
        
        # Weighted severity analysis
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
        
        # Issue type detection
        temp_words = ['température', 'temp', 'chaud', 'surchauffe', 'refroidissement', 'échauffement']
        mech_words = ['vibration', 'bruit', 'usure', 'blocage', 'oscillation']
        elec_words = ['alarme', 'alarm', 'électrique', 'court-circuit', 'arc']
        leak_words = ['fuite', 'étanchéité', 'percement', 'infiltration']
        
        features['has_temperature_issue'] = 1 if any(word in desc_lower for word in temp_words) else 0
        features['has_mechanical_issue'] = 1 if any(word in desc_lower for word in mech_words) else 0
        features['has_electrical_issue'] = 1 if any(word in desc_lower for word in elec_words) else 0
        features['has_leakage_issue'] = 1 if any(word in desc_lower for word in leak_words) else 0
        
        # Text statistics
        features['description_length'] = len(description)
        features['description_word_count'] = len(description.split())
        
        # Urgency analysis
        urgency_words = ['urgent', 'urgence', 'emergency', 'critique', 'arrêt']
        features['urgency_score'] = sum(1 for word in urgency_words if word in desc_lower)
        
        # Complex interactions
        features['equipment_severity_interaction'] = features['equipment_historical_avg'] * features['severe_words_avg_score']
        
        if features['equipment_risk_level'] >= 3 and features['severe_words_count'] > 2:
            features['high_risk_amplifier'] = 1
        else:
            features['high_risk_amplifier'] = 0
        
        features['combined_risk_score'] = (
            (5 - features['equipment_historical_avg']) * 0.4 +
            (5 - features['severe_words_avg_score']) * 0.4 +
            features['severe_words_count'] * 0.2
        )
        
        return features

    def prepare_training_data(self, original_data_file='data/disponibilite.csv'):
        """Prepare training data from historical records"""
        print("Preparing training data...")
        df = pd.read_csv(original_data_file)
        
        X = []
        y = []
        
        for _, row in df.iterrows():
            features = self.extract_features(
                description=row['Description'],
                equipment_name=row['Description de l\'équipement'],
                equipment_id=row['Num_equipement']
            )
            X.append(list(features.values()))
            y.append(row['Disponibilté'])
        
        # Store feature names for later use
        sample_features = self.extract_features("test", "test", "test")
        self.feature_names = list(sample_features.keys())
        
        X = np.array(X)
        y = np.array(y)
        
        print(f"Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y

    def train_model(self, X, y):
        """Train the availability prediction model"""
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        
        print("Training model...")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"Model trained successfully!")
        print(f"Test MAE: {mae:.3f}")
        print(f"Test RMSE: {rmse:.3f}")
        
        # Show feature importance
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        return self.model

    def predict_availability(self, description, equipment_name, equipment_id):
        """Predict equipment availability score"""
        if self.model is None:
            raise ValueError("Model not trained yet! Call train_model() first.")
        
        features = self.extract_features(description, equipment_name, equipment_id)
        X = np.array([list(features.values())])
        
        prediction = self.model.predict(X)[0]
        prediction = max(1, min(5, prediction))  # Clamp between 1 and 5
        
        # Generate explanation
        feature_explanation = {
            'equipment_risk': features['equipment_risk_level'],
            'severe_words_found': features['severe_words_count'],
            'avg_severity_score': round(features['severe_words_avg_score'], 2),
            'combined_risk': round(features['combined_risk_score'], 2),
            'predicted_availability': round(prediction, 2)
        }
        
        return prediction, features, feature_explanation

    def save_model(self, filepath='models/availability_model.pkl'):
        """Save the trained model and data"""
        model_data = {
            'model': self.model,
            'equipment_scores': self.equipment_scores,
            'word_scores': self.word_scores,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath='models/availability_model.pkl'):
        """Load a pre-trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.equipment_scores = model_data['equipment_scores']
        self.word_scores = model_data['word_scores']
        self.feature_names = model_data['feature_names']
        
        print(f"Model loaded from {filepath}")

def main():
    """Main function to train and test the availability prediction system"""
    print("=== AVAILABILITY PREDICTION SYSTEM ===")
    print()
    
    # Initialize and train predictor
    predictor = AvailabilityPredictor()
    predictor.load_historical_data()
    
    X, y = predictor.prepare_training_data()
    predictor.train_model(X, y)
    predictor.save_model()
    
    # Test predictions
    print("\n" + "="*60)
    print("TESTING PREDICTIONS")
    print("="*60)
    
    test_cases = [
        {
            'description': 'Fuite importante détectée avec surchauffe du moteur et vibrations anormales',
            'equipment_name': 'MOTEUR POMPE HYDRAULIQUE',
            'equipment_id': '876b208c-a21b-49d8-9a44-9fbe67dbfd5c'
        },
        {
            'description': 'Contrôle de routine, tout fonctionne normalement',
            'equipment_name': 'CAPTEUR DE VIBRATION',
            'equipment_id': '0bcba8ab-3b66-42ad-be29-e221a1e3e36a'
        },
        {
            'description': 'Alarme critique, panne électrique avec arrêt d\'urgence',
            'equipment_name': 'DISJONCTEUR MT',
            'equipment_id': 'dc5efdf7-c53a-425e-ad96-4cdffe5eb899'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Equipment: {test['equipment_name']}")
        print(f"Description: {test['description']}")
        
        prediction, features, explanation = predictor.predict_availability(
            test['description'],
            test['equipment_name'],
            test['equipment_id']
        )
        
        print(f"\nPredicted Availability: {prediction:.2f}/5")
        print(f"Risk Analysis:")
        print(f" - Equipment Risk Level: {explanation['equipment_risk']}/4")
        print(f" - Severe Words Found: {explanation['severe_words_found']}")
        print(f" - Average Severity Score: {explanation['avg_severity_score']}")
        print(f" - Combined Risk Score: {explanation['combined_risk']}")
        
        if prediction >= 4:
            risk_level = "LOW RISK"
        elif prediction >= 3:
            risk_level = "MEDIUM RISK"
        elif prediction >= 2:
            risk_level = "HIGH RISK"
        else:
            risk_level = "CRITICAL RISK"
        
        print(f" - Risk Level: {risk_level}")

if __name__ == "__main__":
    main()