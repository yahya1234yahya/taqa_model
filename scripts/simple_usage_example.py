from ml_feature_engine
import AvailabilityPredictor

def simple_prediction_example():
    """ print("=== SIMPLE USAGE EXAMPLE ===") predictor = AvailabilityPredictor() try:
    predictor.load_model('models/availability_model.pkl') print("Loaded pre-trained model successfully!")
    except FileNotFoundError:
        print("No pre-trained model found. Training new model...") predictor.load_historical_data() X, y = predictor.prepare_training_data() predictor.train_model(X, y) predictor.save_model() print("\n" + "="*50)
        print("READY FOR PREDICTIONS!") print("="*50) examples = [ { 'description': 'Fuite d\'huile importante avec surchauffe et vibrations anormales', 'equipment_name': 'POMPE HYDRAULIQUE', 'equipment_id': 'test-001' }, { 'description': 'Maintenance préventive - contrôle normal', 'equipment_name': 'CAPTEUR TEMPERATURE', 'equipment_id': 'test-002' }, { 'description': 'Panne critique du moteur avec arrêt d\'urgence', 'equipment_name': 'MOTEUR PRINCIPAL', 'equipment_id': 'test-003' } ] for i, example in enumerate(examples, 1):
        print(f"\n Example {i}:")
        print(f"Equipment: {example['equipment_name']}") print(f"Description: {example['description']}") availability, features, explanation = predictor.predict_availability( example['description'], example['equipment_name'], example['equipment_id'] ) print(f"\n Results:")
        print(f"Predicted Availability: {availability:.2f}/5") if availability >= 4:
        status = " EXCELLENT" elif availability >= 3:
        status = " GOOD" elif availability >= 2:
        status = " MODERATE" else:
        status = " POOR" print(f"Status: {status}")
        print(f"Severe issues detected: {explanation['severe_words_found']}")

def interactive_prediction():
    """ print("\n" + "="*50)
    print("INTERACTIVE PREDICTION MODE") print("="*50) predictor = AvailabilityPredictor() try:
    predictor.load_model('models/availability_model.pkl') except FileNotFoundError:
    print("Training model first...") predictor.load_historical_data() X, y = predictor.prepare_training_data() predictor.train_model(X, y) predictor.save_model() while True:
    print("\n Enter equipment information:") equipment_id = input("Equipment ID: ").strip() if not equipment_id:
    break equipment_name = input("Equipment Name: ").strip() description = input("Anomaly Description: ").strip() if not equipment_name or not description:
    print("Please provide all information!") continue try:
    availability, features, explanation = predictor.predict_availability( description, equipment_name, equipment_id ) print(f"\n PREDICTION RESULTS:")
    print(f"Predicted Availability: {availability:.2f}/5") print(f"Equipment Risk Level: {explanation['equipment_risk']}/4")
    print(f"Severe Words Found: {explanation['severe_words_found']}") print(f"Combined Risk Score: {explanation['combined_risk']}")
    if availability <= 2:
        print(" RECOMMENDATION: Immediate maintenance required!") elif availability <= 3:
        print(" RECOMMENDATION: Schedule maintenance soon") else:
        print(" RECOMMENDATION: Normal operation, monitor regularly")
        except Exception as e:
            print(f"Error making prediction: {e}") continue_input = input("\nMake another prediction? (y/n): ").strip().lower() if continue_input != 'y':
            break if __name__ == "__main__":
            simple_prediction_example() interactive = input("\nWould you like to try interactive mode? (y/n): ").strip().lower() if interactive == 'y':
            interactive_prediction()