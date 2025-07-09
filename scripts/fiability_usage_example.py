from ml_fiability_engine
import FiabilityPredictor

def simple_fiability_prediction():
    """ print("=== FIABILITY PREDICTION EXAMPLE ===") predictor = FiabilityPredictor() try:
    predictor.load_model('models/fiability_model.pkl') print("Loaded pre-trained fiability model successfully!")
    except FileNotFoundError:
        print("No pre-trained model found. Training new fiability model...") predictor.load_historical_data() X, y = predictor.prepare_training_data() predictor.train_model(X, y) predictor.save_model() print("\n" + "="*50)
        print("READY FOR FIABILITY PREDICTIONS!") print("="*50) examples = [ { 'description': 'Vibration anormale avec surchauffe et fuite d\'huile importante', 'equipment_name': 'MOTEUR VENTILATEUR', 'equipment_id': 'test-001' }, { 'description': 'Maintenance préventive - contrôle normal', 'equipment_name': 'CAPTEUR TEMPERATURE', 'equipment_id': 'test-002' }, { 'description': 'Défaillance critique du moteur avec arrêt d\'urgence', 'equipment_name': 'MOTOPOMPE PRINCIPALE', 'equipment_id': 'test-003' } ] for i, example in enumerate(examples, 1):
        print(f"\n Fiability Example {i}:")
        print(f"Equipment: {example['equipment_name']}") print(f"Description: {example['description']}") fiability, features, explanation = predictor.predict_fiability( example['description'], example['equipment_name'], example['equipment_id'] ) print(f"\n Results:")
        print(f"Predicted Fiability: {fiability:.2f}/5") if fiability >= 4:
        status = " EXCELLENT" elif fiability >= 3:
        status = " GOOD" elif fiability >= 2:
        status = " MODERATE" else:
        status = " POOR" print(f"Status: {status}")
        print(f"Severe issues detected: {explanation['severe_words_found']}") if __name__ == "__main__":
        simple_fiability_prediction()