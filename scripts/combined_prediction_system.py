from ml_feature_engine
import AvailabilityPredictor
from ml_fiability_engine
import FiabilityPredictor
import numpy as np

class CombinedEquipmentPredictor:
    """

def __init__(self):
    self.availability_predictor = AvailabilityPredictor() self.fiability_predictor = FiabilityPredictor() self.models_loaded = False

def load_models(self):
    """Load both pre-trained models""" try:
    print("Loading combined prediction models...") self.availability_predictor.load_model('models/availability_model.pkl') print(" Availability model loaded") self.fiability_predictor.load_model('models/fiability_model.pkl') print(" Fiability model loaded") self.models_loaded = True print(" Combined system ready!")
    except FileNotFoundError as e:
        print(f" Model not found: {e}")
        print("Please train the models first using the individual systems.") return False

        return True

def predict_comprehensive(self, description, equipment_name, equipment_id):
    """ if not self.models_loaded:
    raise ValueError("Models not loaded! Call load_models() first.") availability, avail_features, avail_explanation = self.availability_predictor.predict_availability( description, equipment_name, equipment_id ) fiability, fiab_features, fiab_explanation = self.fiability_predictor.predict_fiability( description, equipment_name, equipment_id ) combined_score = (availability + fiability) / 2 if combined_score >= 4.0:
    overall_risk = "LOW RISK" risk_color = "" elif combined_score >= 3.0:
    overall_risk = "MEDIUM RISK" risk_color = "" elif combined_score >= 2.0:
    overall_risk = "HIGH RISK" risk_color = "" else:
    overall_risk = "CRITICAL RISK" risk_color = "" analysis = { 'equipment_id': equipment_id, 'equipment_name': equipment_name, 'description': description, 'availability_score': round(availability, 2), 'fiability_score': round(fiability, 2), 'combined_score': round(combined_score, 2), 'overall_risk': overall_risk, 'risk_color': risk_color, 'availability_analysis': avail_explanation, 'fiability_analysis': fiab_explanation, 'severe_words_availability': avail_explanation['severe_words_found'], 'severe_words_fiability': fiab_explanation['severe_words_found'], 'equipment_risk_availability': avail_explanation['equipment_risk'], 'equipment_risk_fiability': fiab_explanation['equipment_risk'] } return analysis

def get_recommendation(self, analysis):
    """ availability = analysis['availability_score'] fiability = analysis['fiability_score'] combined = analysis['combined_score'] recommendations = [] if combined <= 2:
    recommendations.append(" IMMEDIATE ACTION REQUIRED") recommendations.append("• Stop equipment operation immediately") recommendations.append("• Conduct emergency inspection") recommendations.append("• Contact maintenance team urgently") elif combined <= 3:
    recommendations.append(" HIGH PRIORITY MAINTENANCE") recommendations.append("• Schedule maintenance within 24-48 hours") recommendations.append("• Increase monitoring frequency") recommendations.append("• Prepare replacement parts") elif combined <= 4:
    recommendations.append(" SCHEDULED MAINTENANCE") recommendations.append("• Plan maintenance within next week") recommendations.append("• Monitor performance trends") recommendations.append("• Check operating parameters") else:
    recommendations.append(" NORMAL OPERATIONS") recommendations.append("• Continue normal monitoring") recommendations.append("• Follow standard maintenance schedule") recommendations.append("• Document for trending analysis") if analysis['severe_words_availability'] > 3 or analysis['severe_words_fiability'] > 3:
    recommendations.append("• Multiple severity indicators detected - investigate root cause") equipment_name = analysis['equipment_name'].lower() if 'moteur' in equipment_name or 'motor' in equipment_name:
    recommendations.append("• Check motor temperature and vibration levels") elif 'pompe' in equipment_name or 'pump' in equipment_name:
    recommendations.append("• Verify pump efficiency and seal integrity") elif 'turbine' in equipment_name:
    recommendations.append("• Monitor turbine blade condition and balance") return recommendations

def generate_report(self, analysis):
    """ """ recommendations = self.get_recommendation(analysis) for rec in recommendations:
    report += f"{rec}\n" """ return report

def main():
    """ print("=== COMBINED EQUIPMENT PREDICTION SYSTEM ===")
    print("Predicting both Disponibilité and Fiabilité\n") predictor = CombinedEquipmentPredictor() if not predictor.load_models():
    print("Failed to load models. Please train them first.")
    return print("\n" + "="*60)
    print("COMPREHENSIVE EQUIPMENT ANALYSIS") print("="*60) test_cases = [ { 'description': 'Fuite importante avec surchauffe du moteur et vibrations anormales', 'equipment_name': 'MOTEUR POMPE HYDRAULIQUE', 'equipment_id': '876b208c-a21b-49d8-9a44-9fbe67dbfd5c' }, { 'description': 'Contrôle de routine, maintenance préventive', 'equipment_name': 'CAPTEUR DE VIBRATION', 'equipment_id': '0bcba8ab-3b66-42ad-be29-e221a1e3e36a' }, { 'description': 'Défaillance critique avec arrêt d\'urgence et alarme', 'equipment_name': 'MOTOPOMPE N°1', 'equipment_id': '6bdbbc91-9134-4cd6-aa4b-782df8042214' } ] for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*20} ANALYSIS {i} {'='*20}")
    print(f"Equipment: {test['equipment_name']}") print(f"Description: {test['description']}") analysis = predictor.predict_comprehensive( test['description'], test['equipment_name'], test['equipment_id'] ) print(f"\n PREDICTION RESULTS:")
    print(f"• Availability: {analysis['availability_score']}/5") print(f"• Fiability: {analysis['fiability_score']}/5")
    print(f"• Combined Score: {analysis['combined_score']}/5") print(f"• Risk Level: {analysis['risk_color']} {analysis['overall_risk']}")
    print(f"\n RECOMMENDATIONS:") recommendations = predictor.get_recommendation(analysis) for rec in recommendations[:
    3]: print(f" {rec}")
    print(f"\n Full report available via generate_report() method")

def interactive_mode():
    """ print("\n" + "="*60)
    print("INTERACTIVE COMBINED PREDICTION MODE") print("="*60) predictor = CombinedEquipmentPredictor() if not predictor.load_models():
    return while True:

    print("\n Enter equipment information:") equipment_id = input("Equipment ID: ").strip() if not equipment_id:
    break equipment_name = input("Equipment Name: ").strip() description = input("Issue Description: ").strip() if not equipment_name or not description:
    print("Please provide all information!") continue try:
    analysis = predictor.predict_comprehensive(description, equipment_name, equipment_id) print(f"\n COMPREHENSIVE ANALYSIS:")
    print(f"• Availability: {analysis['availability_score']}/5") print(f"• Fiability: {analysis['fiability_score']}/5")
    print(f"• Combined Score: {analysis['combined_score']}/5") print(f"• Risk Level: {analysis['risk_color']} {analysis['overall_risk']}") recommendations = predictor.get_recommendation(analysis) print(f"\n KEY RECOMMENDATIONS:")
    for rec in recommendations[:
        4]: print(f" {rec}")
        if input("\nGenerate full report? (y/n):
            ").strip().lower() == 'y': report = predictor.generate_report(analysis) print(report)
            except Exception as e:
                print(f"Error making prediction: {e}") continue_input = input("\nAnalyze another equipment? (y/n): ").strip().lower() if continue_input != 'y':
                break if __name__ == "__main__":
                main() interactive = input("\nWould you like to try interactive mode? (y/n): ").strip().lower() if interactive == 'y':
                interactive_mode()