from ml_process_safety_engine import ProcessSafetyPredictor

def simple_process_safety_prediction():
    """
    Simple example of how to use the trained process safety model for predictions
    """
    
    print("=== PROCESS SAFETY PREDICTION EXAMPLE ===")
    
    # Initialize and load pre-trained model
    predictor = ProcessSafetyPredictor()
    
    try:
        # Try to load existing model
        predictor.load_model('process_safety_model.pkl')
        print("Loaded pre-trained process safety model successfully!")
        
    except FileNotFoundError:
        print("No pre-trained model found. Training new process safety model...")
        
        # Load data and train model
        predictor.load_historical_data()
        X, y = predictor.prepare_training_data()
        predictor.train_model(X, y)
        predictor.save_model()
    
    print("\n" + "="*50)
    print("READY FOR PROCESS SAFETY PREDICTIONS")
    print("="*50)
    
    # Example predictions
    examples = [
        {
            'desc': 'Explosion détectée dans l\'unité avec évacuation d\'urgence',
            'equipment': 'Safety System',
            'id': 'SAFETY-001'
        },
        {
            'desc': 'Fuite importante de vapeur toxique avec alarme sécurité',
            'equipment': 'Steam Valve',
            'id': 'VALVE-002'
        },
        {
            'desc': 'Maintenance préventive normale, inspection de routine',
            'equipment': 'Pump Motor',
            'id': 'MOTOR-003'
        },
        {
            'desc': 'Court-circuit électrique avec risque d\'incendie',
            'equipment': 'Electrical Panel',
            'id': 'ELEC-004'
        },
        {
            'desc': 'Vibration anormale détectée, contrôle nécessaire',
            'equipment': 'Turbine',
            'id': 'TURB-005'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n--- Example {i} ---")
        print(f"Equipment: {example['equipment']}")
        print(f"Description: {example['desc']}")
        
        prediction, features, explanation = predictor.predict_process_safety(
            example['desc'], 
            example['equipment'], 
            example['id']
        )
        
        print(f"Predicted Process Safety: {prediction:.2f}/5")
        
        # Safety level interpretation
        if prediction >= 4.0:
            level = "🟢 SAFE"
            action = "Normal operation can continue"
        elif prediction >= 3.0:
            level = "🟡 MODERATE RISK"
            action = "Monitor closely, schedule maintenance"
        elif prediction >= 2.0:
            level = "🟠 HIGH RISK"
            action = "Priority safety review required"
        else:
            level = "🔴 CRITICAL RISK"
            action = "STOP OPERATIONS - Immediate action required"
        
        print(f"Safety Level: {level}")
        print(f"Recommended Action: {action}")
        
        if explanation['catastrophic_hazard']:
            print("⚠️  CATASTROPHIC HAZARD DETECTED!")
        
        print(f"Risk Factors: {explanation['severe_words_found']} severe words found")

def interactive_mode():
    """
    Interactive mode for real-time process safety predictions
    """
    
    print("\n" + "="*50)
    print("INTERACTIVE PROCESS SAFETY PREDICTION MODE")
    print("="*50)
    print("Enter your equipment details for process safety prediction")
    print("Type 'quit' to exit")
    
    # Load pre-trained model
    predictor = ProcessSafetyPredictor()
    try:
        predictor.load_model('process_safety_model.pkl')
        print("✅ Process safety model loaded successfully!")
    except FileNotFoundError:
        print("❌ Model not found. Please run training first.")
        return
    
    while True:
        print("\n" + "-"*30)
        
        # Get user input
        equipment_id = input("Equipment ID: ").strip()
        if equipment_id.lower() == 'quit':
            break
            
        equipment_name = input("Equipment Name/Description: ").strip()
        if equipment_name.lower() == 'quit':
            break
            
        description = input("Anomaly Description: ").strip()
        if description.lower() == 'quit':
            break
        
        if not description:
            print("⚠️  Please provide an anomaly description")
            continue
        
        try:
            # Predict process safety
            prediction, features, explanation = predictor.predict_process_safety(
                description, equipment_name, equipment_id
            )
            
            print(f"\n🔍 PROCESS SAFETY ANALYSIS RESULTS:")
            print(f"   Predicted Process Safety Score: {prediction:.2f}/5")
            
            # Detailed safety analysis
            print(f"\n📊 DETAILED SAFETY ANALYSIS:")
            print(f"   Equipment Risk Level: {explanation['equipment_risk']}/4")
            print(f"   Severe Words Detected: {explanation['severe_words_found']}")
            print(f"   Average Safety Score: {explanation['avg_safety_score']}")
            print(f"   Combined Safety Risk: {explanation['combined_safety_risk']:.2f}")
            print(f"   Catastrophic Hazard: {'YES ⚠️' if explanation['catastrophic_hazard'] else 'NO ✅'}")
            print(f"   Safety Critical Equipment: {'YES' if explanation['safety_critical_equipment'] else 'NO'}")
            
            # Safety recommendations
            print(f"\n🎯 SAFETY RECOMMENDATIONS:")
            if prediction >= 4.0:
                print("   ✅ SAFE - Normal operation can continue")
                print("   📋 Action: Continue routine maintenance")
            elif prediction >= 3.0:
                print("   🟡 MODERATE RISK - Monitor closely")
                print("   📋 Action: Schedule preventive maintenance")
            elif prediction >= 2.0:
                print("   🟠 HIGH RISK - Priority attention needed")
                print("   📋 Action: Immediate safety review required")
            else:
                print("   🔴 CRITICAL RISK - Stop operations")
                print("   📋 Action: Emergency shutdown and investigation")
            
            # Special warnings
            if explanation['catastrophic_hazard']:
                print("   🚨 CATASTROPHIC HAZARD DETECTED - IMMEDIATE ACTION REQUIRED!")
            
            if explanation['severe_words_found'] > 5:
                print("   ⚠️  Multiple severe issues detected - Comprehensive review needed")
                
        except Exception as e:
            print(f"❌ Error during prediction: {e}")
    
    print("\nThank you for using the Process Safety Prediction System!")

if __name__ == "__main__":
    # Run example predictions
    simple_process_safety_prediction()
    
    # Optional: Run interactive mode
    user_input = input("\nWould you like to try interactive mode? (y/n): ").strip().lower()
    if user_input in ['y', 'yes']:
        interactive_mode() 