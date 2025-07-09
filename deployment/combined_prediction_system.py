from ml_feature_engine import AvailabilityPredictor
from ml_fiability_engine import FiabilityPredictor
import numpy as np

class CombinedEquipmentPredictor:
    """
    Combined prediction system for both Disponibilité and Fiabilité
    """
    
    def __init__(self):
        self.availability_predictor = AvailabilityPredictor()
        self.fiability_predictor = FiabilityPredictor()
        self.models_loaded = False
    
    def load_models(self):
        """Load both pre-trained models"""
        
        try:
            print("Loading combined prediction models...")
            
            # Load availability model
            self.availability_predictor.load_model('availability_model.pkl')
            print("✅ Availability model loaded")
            
            # Load fiability model  
            self.fiability_predictor.load_model('fiability_model.pkl')
            print("✅ Fiability model loaded")
            
            self.models_loaded = True
            print("🚀 Combined system ready!")
            
        except FileNotFoundError as e:
            print(f"❌ Model not found: {e}")
            print("Please train the models first using the individual systems.")
            return False
        
        return True
    
    def predict_comprehensive(self, description, equipment_name, equipment_id):
        """
        Make comprehensive predictions for both disponibilité and fiabilité
        
        Args:
            description (str): Anomaly description
            equipment_name (str): Equipment name
            equipment_id (str): Equipment ID
            
        Returns:
            dict: Comprehensive analysis results
        """
        
        if not self.models_loaded:
            raise ValueError("Models not loaded! Call load_models() first.")
        
        # Get availability prediction
        availability, avail_features, avail_explanation = self.availability_predictor.predict_availability(
            description, equipment_name, equipment_id
        )
        
        # Get fiability prediction
        fiability, fiab_features, fiab_explanation = self.fiability_predictor.predict_fiability(
            description, equipment_name, equipment_id
        )
        
        # Calculate combined risk assessment
        combined_score = (availability + fiability) / 2
        
        # Determine overall risk level
        if combined_score >= 4.0:
            overall_risk = "LOW RISK"
            risk_color = "🟢"
        elif combined_score >= 3.0:
            overall_risk = "MEDIUM RISK" 
            risk_color = "🟡"
        elif combined_score >= 2.0:
            overall_risk = "HIGH RISK"
            risk_color = "🟠"
        else:
            overall_risk = "CRITICAL RISK"
            risk_color = "🔴"
        
        # Create comprehensive analysis
        analysis = {
            'equipment_id': equipment_id,
            'equipment_name': equipment_name,
            'description': description,
            
            # Predictions
            'availability_score': round(availability, 2),
            'fiability_score': round(fiability, 2), 
            'combined_score': round(combined_score, 2),
            
            # Risk assessment
            'overall_risk': overall_risk,
            'risk_color': risk_color,
            
            # Detailed analysis
            'availability_analysis': avail_explanation,
            'fiability_analysis': fiab_explanation,
            
            # Severe words detected
            'severe_words_availability': avail_explanation['severe_words_found'],
            'severe_words_fiability': fiab_explanation['severe_words_found'],
            
            # Equipment risk levels
            'equipment_risk_availability': avail_explanation['equipment_risk'],
            'equipment_risk_fiability': fiab_explanation['equipment_risk']
        }
        
        return analysis
    
    def get_recommendation(self, analysis):
        """
        Generate maintenance recommendations based on combined analysis
        """
        
        availability = analysis['availability_score']
        fiability = analysis['fiability_score']
        combined = analysis['combined_score']
        
        recommendations = []
        
        # Critical issues
        if combined <= 2:
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED")
            recommendations.append("• Stop equipment operation immediately")
            recommendations.append("• Conduct emergency inspection")
            recommendations.append("• Contact maintenance team urgently")
        
        # High risk issues
        elif combined <= 3:
            recommendations.append("⚠️ HIGH PRIORITY MAINTENANCE")
            recommendations.append("• Schedule maintenance within 24-48 hours")
            recommendations.append("• Increase monitoring frequency")
            recommendations.append("• Prepare replacement parts")
        
        # Medium risk
        elif combined <= 4:
            recommendations.append("📋 SCHEDULED MAINTENANCE")
            recommendations.append("• Plan maintenance within next week")
            recommendations.append("• Monitor performance trends")
            recommendations.append("• Check operating parameters")
        
        # Low risk
        else:
            recommendations.append("✅ NORMAL OPERATIONS")
            recommendations.append("• Continue normal monitoring")
            recommendations.append("• Follow standard maintenance schedule")
            recommendations.append("• Document for trending analysis")
        
        # Specific recommendations based on severe words
        if analysis['severe_words_availability'] > 3 or analysis['severe_words_fiability'] > 3:
            recommendations.append("• Multiple severity indicators detected - investigate root cause")
        
        # Equipment-specific recommendations
        equipment_name = analysis['equipment_name'].lower()
        if 'moteur' in equipment_name or 'motor' in equipment_name:
            recommendations.append("• Check motor temperature and vibration levels")
        elif 'pompe' in equipment_name or 'pump' in equipment_name:
            recommendations.append("• Verify pump efficiency and seal integrity")
        elif 'turbine' in equipment_name:
            recommendations.append("• Monitor turbine blade condition and balance")
        
        return recommendations
    
    def generate_report(self, analysis):
        """
        Generate a comprehensive equipment analysis report
        """
        
        report = f"""
================================================================================
                        EQUIPMENT ANALYSIS REPORT
================================================================================

Equipment Information:
• ID: {analysis['equipment_id']}
• Name: {analysis['equipment_name']}
• Issue Description: {analysis['description']}

Prediction Results:
• Availability Score: {analysis['availability_score']}/5
• Fiability Score: {analysis['fiability_score']}/5  
• Combined Score: {analysis['combined_score']}/5
• Overall Risk Level: {analysis['risk_color']} {analysis['overall_risk']}

Detailed Analysis:
• Severe Words (Availability): {analysis['severe_words_availability']}
• Severe Words (Fiability): {analysis['severe_words_fiability']}
• Equipment Risk (Availability): {analysis['equipment_risk_availability']}/4
• Equipment Risk (Fiability): {analysis['equipment_risk_fiability']}/4

Recommendations:
"""
        
        recommendations = self.get_recommendation(analysis)
        for rec in recommendations:
            report += f"{rec}\n"
        
        report += f"""
================================================================================
Report generated by Combined Equipment Prediction System
================================================================================
"""
        
        return report

def main():
    """
    Example usage of the combined prediction system
    """
    
    print("=== COMBINED EQUIPMENT PREDICTION SYSTEM ===")
    print("Predicting both Disponibilité and Fiabilité\n")
    
    # Initialize combined system
    predictor = CombinedEquipmentPredictor()
    
    # Load models
    if not predictor.load_models():
        print("Failed to load models. Please train them first.")
        return
    
    print("\n" + "="*60)
    print("COMPREHENSIVE EQUIPMENT ANALYSIS")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            'description': 'Fuite importante avec surchauffe du moteur et vibrations anormales',
            'equipment_name': 'MOTEUR POMPE HYDRAULIQUE',
            'equipment_id': '876b208c-a21b-49d8-9a44-9fbe67dbfd5c'
        },
        {
            'description': 'Contrôle de routine, maintenance préventive',
            'equipment_name': 'CAPTEUR DE VIBRATION',
            'equipment_id': '0bcba8ab-3b66-42ad-be29-e221a1e3e36a'
        },
        {
            'description': 'Défaillance critique avec arrêt d\'urgence et alarme',
            'equipment_name': 'MOTOPOMPE N°1',
            'equipment_id': '6bdbbc91-9134-4cd6-aa4b-782df8042214'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*20} ANALYSIS {i} {'='*20}")
        print(f"Equipment: {test['equipment_name']}")
        print(f"Description: {test['description']}")
        
        # Make comprehensive prediction
        analysis = predictor.predict_comprehensive(
            test['description'],
            test['equipment_name'],
            test['equipment_id']
        )
        
        # Display results
        print(f"\n📊 PREDICTION RESULTS:")
        print(f"• Availability: {analysis['availability_score']}/5")
        print(f"• Fiability: {analysis['fiability_score']}/5")
        print(f"• Combined Score: {analysis['combined_score']}/5")
        print(f"• Risk Level: {analysis['risk_color']} {analysis['overall_risk']}")
        
        # Show recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        recommendations = predictor.get_recommendation(analysis)
        for rec in recommendations[:3]:  # Show first 3 recommendations
            print(f"  {rec}")
        
        # Generate full report option
        print(f"\n📄 Full report available via generate_report() method")

def interactive_mode():
    """
    Interactive mode for user input
    """
    
    print("\n" + "="*60)
    print("INTERACTIVE COMBINED PREDICTION MODE")
    print("="*60)
    
    # Load models
    predictor = CombinedEquipmentPredictor()
    if not predictor.load_models():
        return
    
    while True:
        print("\n📝 Enter equipment information:")
        
        equipment_id = input("Equipment ID: ").strip()
        if not equipment_id:
            break
            
        equipment_name = input("Equipment Name: ").strip()
        description = input("Issue Description: ").strip()
        
        if not equipment_name or not description:
            print("Please provide all information!")
            continue
        
        try:
            # Make comprehensive prediction
            analysis = predictor.predict_comprehensive(description, equipment_name, equipment_id)
            
            print(f"\n📊 COMPREHENSIVE ANALYSIS:")
            print(f"• Availability: {analysis['availability_score']}/5")
            print(f"• Fiability: {analysis['fiability_score']}/5") 
            print(f"• Combined Score: {analysis['combined_score']}/5")
            print(f"• Risk Level: {analysis['risk_color']} {analysis['overall_risk']}")
            
            # Show top recommendations
            recommendations = predictor.get_recommendation(analysis)
            print(f"\n💡 KEY RECOMMENDATIONS:")
            for rec in recommendations[:4]:
                print(f"  {rec}")
            
            # Offer full report
            if input("\nGenerate full report? (y/n): ").strip().lower() == 'y':
                report = predictor.generate_report(analysis)
                print(report)
                
        except Exception as e:
            print(f"Error making prediction: {e}")
        
        continue_input = input("\nAnalyze another equipment? (y/n): ").strip().lower()
        if continue_input != 'y':
            break

if __name__ == "__main__":
    # Run main example
    main()
    
    # Ask if user wants interactive mode
    interactive = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
    if interactive == 'y':
        interactive_mode() 