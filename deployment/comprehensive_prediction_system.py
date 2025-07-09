from ml_feature_engine import AvailabilityPredictor
from ml_fiability_engine import FiabilityPredictor
from ml_process_safety_engine import ProcessSafetyPredictor
import numpy as np

class ComprehensiveEquipmentPredictor:
    """
    Comprehensive prediction system for Disponibilité, Fiabilité, and Process Safety
    """
    
    def __init__(self):
        self.availability_predictor = AvailabilityPredictor()
        self.fiability_predictor = FiabilityPredictor()
        self.process_safety_predictor = ProcessSafetyPredictor()
        self.models_loaded = False
    
    def load_models(self):
        """Load all three pre-trained models"""
        
        try:
            print("Loading comprehensive prediction models...")
            
            # Load availability model
            self.availability_predictor.load_model('availability_model.pkl')
            print("✅ Availability model loaded")
            
            # Load fiability model
            self.fiability_predictor.load_model('fiability_model.pkl')
            print("✅ Fiability model loaded")
            
            # Load process safety model
            self.process_safety_predictor.load_model('process_safety_model.pkl')
            print("✅ Process safety model loaded")
            
            self.models_loaded = True
            print("🎉 All models loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"❌ Model file not found: {e}")
            print("Please ensure all models are trained and saved first.")
            return False
        
        return True
    
    def train_all_models(self):
        """Train all three models if they don't exist"""
        
        print("Training all prediction models...")
        
        try:
            # Train availability model
            print("\n1. Training Availability Model...")
            self.availability_predictor.load_historical_data()
            X_avail, y_avail = self.availability_predictor.prepare_training_data()
            self.availability_predictor.train_model(X_avail, y_avail)
            self.availability_predictor.save_model()
            
            # Train fiability model
            print("\n2. Training Fiability Model...")
            self.fiability_predictor.load_historical_data()
            X_fiab, y_fiab = self.fiability_predictor.prepare_training_data()
            self.fiability_predictor.train_model(X_fiab, y_fiab)
            self.fiability_predictor.save_model()
            
            # Train process safety model
            print("\n3. Training Process Safety Model...")
            self.process_safety_predictor.load_historical_data()
            X_safety, y_safety = self.process_safety_predictor.prepare_training_data()
            self.process_safety_predictor.train_model(X_safety, y_safety)
            self.process_safety_predictor.save_model()
            
            self.models_loaded = True
            print("\n🎉 All models trained and saved successfully!")
            
        except Exception as e:
            print(f"❌ Error during training: {e}")
            return False
        
        return True
    
    def predict_all(self, description, equipment_name, equipment_id):
        """
        Comprehensive prediction for all three metrics
        
        Args:
            description (str): Anomaly description
            equipment_name (str): Equipment name/description
            equipment_id (str): Equipment unique identifier
            
        Returns:
            dict: Complete analysis results
        """
        
        if not self.models_loaded:
            raise ValueError("Models not loaded! Call load_models() or train_all_models() first.")
        
        try:
            # Get predictions from all three models
            avail_pred, avail_features, avail_explanation = self.availability_predictor.predict_availability(
                description, equipment_name, equipment_id
            )
            
            fiab_pred, fiab_features, fiab_explanation = self.fiability_predictor.predict_fiability(
                description, equipment_name, equipment_id
            )
            
            safety_pred, safety_features, safety_explanation = self.process_safety_predictor.predict_process_safety(
                description, equipment_name, equipment_id
            )
            
            # Calculate overall equipment health score
            overall_score = (avail_pred + fiab_pred + safety_pred) / 3
            
            # Determine critical factors
            critical_factors = []
            if avail_pred < 2.5:
                critical_factors.append("Low Availability")
            if fiab_pred < 2.5:
                critical_factors.append("Low Reliability")
            if safety_pred < 2.5:
                critical_factors.append("Safety Risk")
            
            # Determine overall risk level
            min_score = min(avail_pred, fiab_pred, safety_pred)
            if min_score >= 4.0:
                risk_level = "LOW"
                risk_color = "🟢"
                action = "Continue normal operation"
            elif min_score >= 3.0:
                risk_level = "MODERATE"
                risk_color = "🟡"
                action = "Monitor and schedule maintenance"
            elif min_score >= 2.0:
                risk_level = "HIGH"
                risk_color = "🟠"
                action = "Priority intervention required"
            else:
                risk_level = "CRITICAL"
                risk_color = "🔴"
                action = "Immediate action required"
            
            # Comprehensive analysis results
            comprehensive_results = {
                'predictions': {
                    'availability': round(avail_pred, 2),
                    'fiability': round(fiab_pred, 2),
                    'process_safety': round(safety_pred, 2),
                    'overall_score': round(overall_score, 2)
                },
                'risk_assessment': {
                    'overall_risk_level': risk_level,
                    'risk_color': risk_color,
                    'recommended_action': action,
                    'critical_factors': critical_factors,
                    'weakest_aspect': 'availability' if avail_pred <= min(fiab_pred, safety_pred) else 
                                    'fiability' if fiab_pred <= min(avail_pred, safety_pred) else 'process_safety'
                },
                'detailed_analysis': {
                    'availability': {
                        'score': round(avail_pred, 2),
                        'severe_words': avail_explanation.get('severe_words_found', 0),
                        'equipment_risk': avail_explanation.get('equipment_risk', 0),
                        'prediction_confidence': avail_explanation.get('prediction_confidence', 'medium')
                    },
                    'fiability': {
                        'score': round(fiab_pred, 2),
                        'severe_words': fiab_explanation.get('severe_words_found', 0),
                        'equipment_risk': fiab_explanation.get('equipment_risk', 0),
                        'prediction_confidence': fiab_explanation.get('prediction_confidence', 'medium')
                    },
                    'process_safety': {
                        'score': round(safety_pred, 2),
                        'severe_words': safety_explanation.get('severe_words_found', 0),
                        'equipment_risk': safety_explanation.get('equipment_risk', 0),
                        'catastrophic_hazard': safety_explanation.get('catastrophic_hazard', False),
                        'safety_critical_equipment': safety_explanation.get('safety_critical_equipment', False)
                    }
                },
                'maintenance_recommendations': self._generate_maintenance_recommendations(
                    avail_pred, fiab_pred, safety_pred, critical_factors
                )
            }
            
            return comprehensive_results
            
        except Exception as e:
            print(f"❌ Error during comprehensive prediction: {e}")
            raise
    
    def _generate_maintenance_recommendations(self, avail_pred, fiab_pred, safety_pred, critical_factors):
        """Generate specific maintenance recommendations based on all predictions"""
        
        recommendations = []
        
        # Safety-first approach
        if safety_pred < 2.0:
            recommendations.append("🚨 CRITICAL: Immediate safety assessment required")
            recommendations.append("🛑 STOP operations until safety issues are resolved")
        elif safety_pred < 2.5:
            recommendations.append("⚠️  HIGH PRIORITY: Safety review within 24 hours")
        
        # Availability recommendations
        if avail_pred < 2.0:
            recommendations.append("🔧 URGENT: Equipment likely to fail soon - schedule immediate maintenance")
        elif avail_pred < 2.5:
            recommendations.append("📅 PRIORITY: Schedule maintenance within this week")
        elif avail_pred < 3.5:
            recommendations.append("📋 PLANNED: Include in next maintenance cycle")
        
        # Fiability recommendations
        if fiab_pred < 2.0:
            recommendations.append("🏭 RELIABILITY: Equipment showing signs of degradation - investigate root causes")
        elif fiab_pred < 2.5:
            recommendations.append("🔍 MONITOR: Increase inspection frequency")
        
        # Combined recommendations
        if len(critical_factors) >= 2:
            recommendations.append("🚨 MULTI-FACTOR RISK: Comprehensive equipment overhaul needed")
        
        # Positive recommendations
        if min(avail_pred, fiab_pred, safety_pred) >= 4.0:
            recommendations.append("✅ EXCELLENT: Equipment in good condition - continue current maintenance schedule")
        elif min(avail_pred, fiab_pred, safety_pred) >= 3.5:
            recommendations.append("✅ GOOD: Equipment performing well - monitor regularly")
        
        return recommendations
    
    def generate_report(self, description, equipment_name, equipment_id, include_details=True):
        """
        Generate a comprehensive analysis report
        """
        
        print("=" * 80)
        print("🏭 COMPREHENSIVE EQUIPMENT ANALYSIS REPORT")
        print("=" * 80)
        
        print(f"\n📋 EQUIPMENT INFORMATION:")
        print(f"   Equipment ID: {equipment_id}")
        print(f"   Equipment Name: {equipment_name}")
        print(f"   Issue Description: {description}")
        
        # Get comprehensive predictions
        results = self.predict_all(description, equipment_name, equipment_id)
        
        print(f"\n📊 PREDICTION RESULTS:")
        print(f"   Availability Score:    {results['predictions']['availability']}/5")
        print(f"   Fiability Score:       {results['predictions']['fiability']}/5")
        print(f"   Process Safety Score:  {results['predictions']['process_safety']}/5")
        print(f"   Overall Health Score:  {results['predictions']['overall_score']}/5")
        
        print(f"\n🎯 RISK ASSESSMENT:")
        print(f"   Overall Risk Level: {results['risk_assessment']['risk_color']} {results['risk_assessment']['overall_risk_level']}")
        print(f"   Recommended Action: {results['risk_assessment']['recommended_action']}")
        
        if results['risk_assessment']['critical_factors']:
            print(f"   Critical Factors: {', '.join(results['risk_assessment']['critical_factors'])}")
        
        print(f"   Weakest Aspect: {results['risk_assessment']['weakest_aspect'].title()}")
        
        if include_details:
            print(f"\n🔍 DETAILED ANALYSIS:")
            
            # Availability details
            avail = results['detailed_analysis']['availability']
            print(f"   Availability ({avail['score']}/5):")
            print(f"     - Equipment Risk Level: {avail['equipment_risk']}/4")
            print(f"     - Severe Words Found: {avail['severe_words']}")
            
            # Fiability details
            fiab = results['detailed_analysis']['fiability']
            print(f"   Fiability ({fiab['score']}/5):")
            print(f"     - Equipment Risk Level: {fiab['equipment_risk']}/4")
            print(f"     - Severe Words Found: {fiab['severe_words']}")
            
            # Process Safety details
            safety = results['detailed_analysis']['process_safety']
            print(f"   Process Safety ({safety['score']}/5):")
            print(f"     - Equipment Risk Level: {safety['equipment_risk']}/4")
            print(f"     - Severe Words Found: {safety['severe_words']}")
            print(f"     - Catastrophic Hazard: {'YES ⚠️' if safety['catastrophic_hazard'] else 'NO ✅'}")
            print(f"     - Safety Critical: {'YES' if safety['safety_critical_equipment'] else 'NO'}")
        
        print(f"\n📋 MAINTENANCE RECOMMENDATIONS:")
        for i, recommendation in enumerate(results['maintenance_recommendations'], 1):
            print(f"   {i}. {recommendation}")
        
        print("\n" + "=" * 80)
        
        return results

def main():
    """
    Demonstration of the comprehensive prediction system
    """
    
    print("🏭 COMPREHENSIVE EQUIPMENT PREDICTION SYSTEM")
    print("Predicting Availability, Fiability, and Process Safety")
    print("=" * 60)
    
    # Initialize comprehensive predictor
    predictor = ComprehensiveEquipmentPredictor()
    
    # Try to load existing models
    if not predictor.load_models():
        print("\nTraining all models from scratch...")
        if not predictor.train_all_models():
            print("❌ Failed to train models. Exiting.")
            return
    
    print("\n" + "="*60)
    print("COMPREHENSIVE PREDICTION EXAMPLES")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            'description': 'Explosion détectée avec fuite importante et arrêt d\'urgence',
            'equipment_name': 'Steam Safety System',
            'equipment_id': 'SAFETY-CRITICAL-001'
        },
        {
            'description': 'Vibration anormale avec bruit suspect au niveau du palier',
            'equipment_name': 'Turbine Generator',
            'equipment_id': '52b20517-a1ba-4b78-8711-adebd336a6c2'
        },
        {
            'description': 'Maintenance préventive normale, contrôle de routine',
            'equipment_name': 'Pump Motor',
            'equipment_id': 'MOTOR-STANDARD-001'
        },
        {
            'description': 'Alarme critique température élevée avec surchauffe moteur',
            'equipment_name': 'Fan Motor',
            'equipment_id': 'e1768504-8b0f-4753-b9d8-35888de02a4b'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔸 TEST CASE {i}:")
        
        try:
            results = predictor.generate_report(
                test_case['description'],
                test_case['equipment_name'],
                test_case['equipment_id'],
                include_details=False  # Set to True for full details
            )
            
            # Quick summary
            risk_level = results['risk_assessment']['overall_risk_level']
            if risk_level == "CRITICAL":
                print("🚨 IMMEDIATE ACTION REQUIRED!")
            elif risk_level == "HIGH":
                print("⚠️  HIGH PRIORITY INTERVENTION NEEDED")
            elif risk_level == "MODERATE":
                print("📋 MONITOR AND SCHEDULE MAINTENANCE")
            else:
                print("✅ EQUIPMENT IN GOOD CONDITION")
                
        except Exception as e:
            print(f"❌ Error analyzing test case {i}: {e}")
    
    print(f"\n🎉 Comprehensive analysis complete!")
    print(f"💡 All three models (Availability, Fiability, Process Safety) working together")
    print(f"📊 Ready for production use!")

if __name__ == "__main__":
    main() 