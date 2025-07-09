from flask import Flask, request, jsonify
import traceback
import time
import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from comprehensive_prediction_system import ComprehensiveEquipmentPredictor
from training_manager import training_manager

app = Flask(__name__)

# Initialize the predictor globally
predictor = None

def initialize_models():
    """Initialize all ML models"""
    global predictor
    try:
        print("Loading ML models...")
        predictor = ComprehensiveEquipmentPredictor()
        predictor.load_models()
        print("✅ All models loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print(f"❌ App will start but predictions will not work")
        traceback.print_exc()
        # Don't exit in production - let the app start but return errors
        predictor = None
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    models_loaded = predictor is not None
    status = "healthy" if models_loaded else "degraded"
    message = "Equipment Prediction API is running"
    
    if not models_loaded:
        message = "API is running but ML models failed to load"
    
    return jsonify({
        "status": status,
        "models_loaded": models_loaded,
        "message": message,
        "app_name": "Equipment Prediction API",
        "version": "1.0.0"
    })

def validate_anomaly_data(anomaly_data, index=None):
    """Validate a single anomaly data object"""
    if not isinstance(anomaly_data, dict):
        return f"Anomaly{f' at index {index}' if index is not None else ''} must be an object"
    
    required_fields = ['anomaly_id', 'description', 'equipment_name', 'equipment_id']
    missing_fields = []
    
    for field in required_fields:
        if not anomaly_data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        return f"Missing required fields{f' at index {index}' if index is not None else ''}: {missing_fields}"
    
    return None

def process_single_anomaly(anomaly_data):
    """Process a single anomaly and return results"""
    try:
        results = predictor.predict_all(
            description=anomaly_data['description'],
            equipment_name=anomaly_data['equipment_name'], 
            equipment_id=anomaly_data['equipment_id']
        )
        
        return {
            "anomaly_id": anomaly_data['anomaly_id'],
            "equipment_id": anomaly_data['equipment_id'],
            "equipment_name": anomaly_data['equipment_name'],
            "predictions": {
                "availability": {
                    "score": round(results['predictions']['availability']),
                    "description": "Equipment uptime and operational readiness"
                },
                "reliability": {
                    "score": round(results['predictions']['fiability']), 
                    "description": "Equipment integrity and dependability"
                },
                "process_safety": {
                    "score": round(results['predictions']['process_safety']),
                    "description": "Safety risk assessment and hazard identification"
                }
            },
            "overall_score": round(results['predictions']['overall_score']),
            "risk_assessment": {
                "overall_risk_level": results['risk_assessment']['overall_risk_level'],
                "recommended_action": results['risk_assessment']['recommended_action'],
                "critical_factors": results['risk_assessment']['critical_factors'],
                "weakest_aspect": results['risk_assessment']['weakest_aspect']
            },
            "maintenance_recommendations": results['maintenance_recommendations'],
            "status": "success"
        }
    except Exception as e:
        return {
            "anomaly_id": anomaly_data.get('anomaly_id', 'unknown'),
            "equipment_id": anomaly_data.get('equipment_id', 'unknown'),
            "equipment_name": anomaly_data.get('equipment_name', 'unknown'),
            "status": "error",
            "error": str(e)
        }

@app.route('/predict', methods=['POST'])
def predict_anomaly():
    """
    Predict equipment anomaly scores for single or multiple anomalies
    
    Expected JSON payload for single anomaly:
    {
        "anomaly_id": "unique_id_for_this_anomaly",
        "description": "anomaly description text",
        "equipment_name": "equipment name/description", 
        "equipment_id": "equipment UUID"
    }
    
    Expected JSON payload for multiple anomalies:
    [
        {
            "anomaly_id": "anomaly_1",
            "description": "first anomaly description",
            "equipment_name": "equipment 1",
            "equipment_id": "uuid_1"
        },
        {
            "anomaly_id": "anomaly_2", 
            "description": "second anomaly description",
            "equipment_name": "equipment 2",
            "equipment_id": "uuid_2"
        }
        // ... up to 6000 anomalies
    ]
    """
    try:
        # Check if models are loaded
        if predictor is None:
            return jsonify({
                "error": "Models not loaded",
                "message": "ML models are not initialized"
            }), 500
        
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "message": "Please send JSON data in request body"
            }), 400
        
        start_time = time.time()
        
        # Determine if we have single anomaly or multiple anomalies
        if isinstance(data, list):
            # Multiple anomalies (batch processing)
            print(f"🔄 Processing batch of {len(data)} anomalies...")
            
            if len(data) == 0:
                return jsonify({
                    "error": "Empty anomaly list",
                    "message": "Please provide at least one anomaly"
                }), 400
            
            if len(data) > 6000:
                return jsonify({
                    "error": "Too many anomalies",
                    "message": f"Maximum 6000 anomalies allowed, got {len(data)}"
                }), 400
            
            # Validate all anomalies first
            validation_errors = []
            for i, anomaly in enumerate(data):
                error = validate_anomaly_data(anomaly, i)
                if error:
                    validation_errors.append(error)
            
            if validation_errors:
                return jsonify({
                    "error": "Validation failed",
                    "validation_errors": validation_errors,
                    "message": "Please fix the validation errors"
                }), 400
            
            # Process all anomalies
            results = []
            successful_predictions = 0
            failed_predictions = 0
            
            for i, anomaly in enumerate(data):
                if i % 100 == 0:  # Progress logging every 100 items
                    print(f"📊 Progress: {i}/{len(data)} anomalies processed")
                
                result = process_single_anomaly(anomaly)
                results.append(result)
                
                if result['status'] == 'success':
                    successful_predictions += 1
                else:
                    failed_predictions += 1
            
            processing_time = round(time.time() - start_time, 2)
            
            response = {
                "batch_info": {
                    "total_anomalies": len(data),
                    "successful_predictions": successful_predictions,
                    "failed_predictions": failed_predictions,
                    "processing_time_seconds": processing_time,
                    "average_time_per_anomaly": round(processing_time / len(data), 3)
                },
                "results": results,
                "status": "completed"
            }
            
            print(f"✅ Batch processing completed: {successful_predictions} successful, {failed_predictions} failed in {processing_time}s")
            return jsonify(response)
            
        else:
            # Single anomaly (backward compatibility)
            print(f"🔄 Processing single anomaly...")
            
            # Validate single anomaly
            error = validate_anomaly_data(data)
            if error:
                return jsonify({
                    "error": "Validation failed",
                    "message": error
                }), 400
            
            # Process single anomaly
            print(f"Making predictions for anomaly: {data['anomaly_id']}")
            print(f"Description: {data['description'][:100]}...")  # Log first 100 chars
            
            result = process_single_anomaly(data)
            processing_time = round(time.time() - start_time, 3)
            result["processing_time_seconds"] = processing_time
            
            if result['status'] == 'success':
                print(f"✅ Predictions completed for anomaly: {data['anomaly_id']} in {processing_time}s")
            else:
                print(f"❌ Prediction failed for anomaly: {data['anomaly_id']}")
            
            return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Prediction failed", 
            "message": str(e),
            "status": "error"
        }), 500

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check system status"""
    import os
    import sys
    
    # Check file existence
    required_files = [
        'availability_model.pkl',
        'fiability_model.pkl', 
        'process_safety_model.pkl',
        'equipment_simple.csv',
        'severe_words_simple.csv'
    ]
    
    file_status = {}
    for file in required_files:
        file_status[file] = {
            "exists": os.path.exists(file),
            "size_mb": round(os.path.getsize(file) / 1024 / 1024, 2) if os.path.exists(file) else 0
        }
    
    return jsonify({
        "predictor_loaded": predictor is not None,
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "files": file_status,
        "environment": dict(os.environ)
    })

@app.route('/models/info', methods=['GET'])
def models_info():
    """Get information about loaded models"""
    if predictor is None:
        return jsonify({
            "error": "Models not loaded",
            "models_loaded": False
        }), 500
    
    return jsonify({
        "models_loaded": True,
        "models": {
            "availability": {
                "description": "Predicts equipment uptime and operational readiness",
                "features": 23,
                "target_range": "1-5 (higher = better availability)"
            },
            "reliability": {
                "description": "Predicts equipment integrity and dependability", 
                "features": 23,
                "target_range": "1-5 (higher = better reliability)"
            },
            "process_safety": {
                "description": "Predicts safety risk assessment and hazard identification",
                "features": 29, 
                "target_range": "1-5 (higher = better safety)"
            }
        },
        "usage": {
            "endpoint": "/predict",
            "method": "POST",
            "supports": "Single anomaly object OR array of anomaly objects (max 6000)",
            "required_fields": ["anomaly_id", "description", "equipment_name", "equipment_id"],
            "batch_processing": "Automatically detects single vs multiple anomalies"
        }
    })

@app.route('/models/metrics', methods=['GET'])
def model_metrics():
    """
    Get comprehensive model performance metrics and statistics
    
    Returns detailed metrics including:
    - Model accuracy and performance metrics (MAE, MSE, R2)
    - Training data statistics and distribution
    - Model file information (size, last modified)
    - Training history and trends
    - Data quality indicators
    """
    try:
        if predictor is None:
            return jsonify({
                "error": "Models not loaded",
                "models_loaded": False
            }), 500
        
        print("📊 Calculating model metrics...")
        
        # Initialize metrics structure
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "models_loaded": True,
            "model_performance": {},
            "training_statistics": {},
            "data_quality": {},
            "model_files": {},
            "training_history": {},
            "summary": {}
        }
        
        # === MODEL FILE INFORMATION ===
        model_files = {
            'availability': 'availability_model.pkl',
            'fiability': 'fiability_model.pkl',
            'process_safety': 'process_safety_model.pkl'
        }
        
        for model_type, filename in model_files.items():
            if os.path.exists(filename):
                stat = os.stat(filename)
                metrics["model_files"][model_type] = {
                    "filename": filename,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "exists": True
                }
            else:
                metrics["model_files"][model_type] = {
                    "filename": filename,
                    "exists": False
                }
        
        # === TRAINING DATA STATISTICS ===
        data_files = {
            'availability': 'disponibilite.csv',
            'fiability': 'fiabilite.csv', 
            'process_safety': 'process_safty.csv'
        }
        
        for model_type, filename in data_files.items():
            if os.path.exists(filename):
                try:
                    df = pd.read_csv(filename)
                    target_cols = {
                        'availability': 'Disponibilté',
                        'fiability': 'Fiabilité Intégrité',
                        'process_safety': 'Process Safety'
                    }
                    
                    target_col = target_cols[model_type]
                    if target_col in df.columns:
                        target_data = df[target_col].dropna()
                        
                        metrics["training_statistics"][model_type] = {
                            "total_records": len(df),
                            "valid_target_records": len(target_data),
                            "target_distribution": {
                                "score_1": int(sum(target_data == 1)),
                                "score_2": int(sum(target_data == 2)),
                                "score_3": int(sum(target_data == 3)),
                                "score_4": int(sum(target_data == 4)),
                                "score_5": int(sum(target_data == 5))
                            },
                            "target_statistics": {
                                "mean": round(float(target_data.mean()), 3),
                                "std": round(float(target_data.std()), 3),
                                "min": int(target_data.min()),
                                "max": int(target_data.max()),
                                "median": float(target_data.median())
                            },
                            "data_quality": {
                                "missing_descriptions": int(df['Description'].isna().sum()),
                                "missing_equipment_ids": int(df['Num_equipement'].isna().sum()),
                                "missing_targets": int(df[target_col].isna().sum()),
                                "duplicate_records": int(df.duplicated().sum())
                            }
                        }
                except Exception as e:
                    metrics["training_statistics"][model_type] = {
                        "error": f"Failed to analyze {filename}: {str(e)}"
                    }
            else:
                metrics["training_statistics"][model_type] = {
                    "error": f"Training data file {filename} not found"
                }
        
        # === MODEL PERFORMANCE EVALUATION ===
        for model_type in ['availability', 'fiability', 'process_safety']:
            try:
                # Use recent data for evaluation (last 20% of records)
                data_file = data_files[model_type]
                if os.path.exists(data_file):
                    df = pd.read_csv(data_file)
                    target_cols = {
                        'availability': 'Disponibilté',
                        'fiability': 'Fiabilité Intégrité',
                        'process_safety': 'Process Safety'
                    }
                    target_col = target_cols[model_type]
                    
                    if target_col in df.columns and len(df) > 50:
                        # Use last 20% as test set (minimum 10, maximum 200 records)
                        test_size = max(10, min(200, int(len(df) * 0.2)))
                        test_df = df.tail(test_size).copy()
                        
                        # Get predictions for test set
                        predictions = []
                        actuals = []
                        
                        for _, row in test_df.iterrows():
                            try:
                                if model_type == 'availability':
                                    pred, _, _ = predictor.availability_predictor.predict_availability(
                                        row['Description'], 
                                        row['Description de l\'équipement'], 
                                        row['Num_equipement']
                                    )
                                elif model_type == 'fiability':
                                    pred, _, _ = predictor.fiability_predictor.predict_fiability(
                                        row['Description'], 
                                        row['Description de l\'équipement'], 
                                        row['Num_equipement']
                                    )
                                else:  # process_safety
                                    pred, _, _ = predictor.process_safety_predictor.predict_process_safety(
                                        row['Description'], 
                                        row['Description de l\'équipement'], 
                                        row['Num_equipement']
                                    )
                                
                                predictions.append(pred)
                                actuals.append(row[target_col])
                            except:
                                continue
                        
                        if len(predictions) > 5:  # Need at least 5 predictions for meaningful metrics
                            predictions = np.array(predictions)
                            actuals = np.array(actuals)
                            
                            # Calculate regression metrics
                            mae = mean_absolute_error(actuals, predictions)
                            mse = mean_squared_error(actuals, predictions)
                            rmse = np.sqrt(mse)
                            r2 = r2_score(actuals, predictions)
                            
                            # Calculate custom accuracy (within 0.5 score range)
                            accuracy_05 = np.mean(np.abs(predictions - actuals) <= 0.5) * 100
                            accuracy_10 = np.mean(np.abs(predictions - actuals) <= 1.0) * 100
                            
                            # Calculate bias
                            bias = np.mean(predictions - actuals)
                            
                            metrics["model_performance"][model_type] = {
                                "test_samples": len(predictions),
                                "regression_metrics": {
                                    "mae": round(mae, 4),
                                    "mse": round(mse, 4),
                                    "rmse": round(rmse, 4),
                                    "r2_score": round(r2, 4)
                                },
                                "accuracy_metrics": {
                                    "accuracy_within_0.5": round(accuracy_05, 2),
                                    "accuracy_within_1.0": round(accuracy_10, 2)
                                },
                                "prediction_statistics": {
                                    "mean_prediction": round(float(np.mean(predictions)), 3),
                                    "mean_actual": round(float(np.mean(actuals)), 3),
                                    "bias": round(bias, 4),
                                    "prediction_std": round(float(np.std(predictions)), 3),
                                    "actual_std": round(float(np.std(actuals)), 3)
                                },
                                "score_distribution": {
                                    "predicted": {
                                        f"score_{i}": int(np.sum((predictions >= i-0.5) & (predictions < i+0.5)))
                                        for i in range(1, 6)
                                    },
                                    "actual": {
                                        f"score_{i}": int(np.sum(actuals == i))
                                        for i in range(1, 6)
                                    }
                                }
                            }
                        else:
                            metrics["model_performance"][model_type] = {
                                "error": "Insufficient test data for evaluation"
                            }
                    else:
                        metrics["model_performance"][model_type] = {
                            "error": "Insufficient training data for evaluation"
                        }
                else:
                    metrics["model_performance"][model_type] = {
                        "error": f"Training data file not found: {data_file}"
                    }
            except Exception as e:
                metrics["model_performance"][model_type] = {
                    "error": f"Performance evaluation failed: {str(e)}"
                }
        
        # === TRAINING HISTORY ===
        training_status = training_manager.get_training_status()
        metrics["training_history"] = {
            "total_training_sessions": training_status["training_sessions_completed"],
            "last_training": training_status["last_training"],
            "available_backups": training_status["available_backups"],
            "is_currently_training": training_status["is_training"]
        }
        
        # === OVERALL SUMMARY ===
        # Calculate overall model health score
        performance_scores = []
        for model_type in ['availability', 'fiability', 'process_safety']:
            if model_type in metrics["model_performance"] and "regression_metrics" in metrics["model_performance"][model_type]:
                r2 = metrics["model_performance"][model_type]["regression_metrics"]["r2_score"]
                acc_05 = metrics["model_performance"][model_type]["accuracy_metrics"]["accuracy_within_0.5"]
                # Combine R2 and accuracy for overall score
                model_score = (r2 * 50) + (acc_05 * 0.5)  # Scale to 0-100
                performance_scores.append(max(0, min(100, model_score)))
        
        overall_health = np.mean(performance_scores) if performance_scores else 0
        
        # Determine health status
        if overall_health >= 80:
            health_status = "EXCELLENT"
        elif overall_health >= 70:
            health_status = "GOOD"
        elif overall_health >= 60:
            health_status = "FAIR"
        elif overall_health >= 40:
            health_status = "POOR"
        else:
            health_status = "CRITICAL"
        
        metrics["summary"] = {
            "overall_model_health": round(overall_health, 2),
            "health_status": health_status,
            "models_evaluated": len(performance_scores),
            "total_training_records": sum([
                metrics["training_statistics"][model]["total_records"] 
                for model in metrics["training_statistics"] 
                if "total_records" in metrics["training_statistics"][model]
            ]),
            "recommendations": []
        }
        
        # Add recommendations based on metrics
        if overall_health < 70:
            metrics["summary"]["recommendations"].append("Consider retraining models with more diverse data")
        
        if metrics["training_history"]["total_training_sessions"] == 0:
            metrics["summary"]["recommendations"].append("No incremental training performed yet - consider training with new data")
        
        for model_type in metrics["training_statistics"]:
            if "data_quality" in metrics["training_statistics"][model_type]:
                quality = metrics["training_statistics"][model_type]["data_quality"]
                if quality["missing_descriptions"] > quality.get("total_records", 0) * 0.1:
                    metrics["summary"]["recommendations"].append(f"High missing description rate in {model_type} data - data quality improvement needed")
        
        print("✅ Model metrics calculated successfully")
        return jsonify(metrics), 200
        
    except Exception as e:
        print(f"❌ Error calculating model metrics: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Failed to calculate model metrics",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/train', methods=['POST'])
def train_models():
    """
    Train models with new anomaly data
    
    Expected JSON payload:
    [
        {
            "anomaly_id": "unique_id",
            "description": "anomaly description", 
            "equipment_name": "equipment name",
            "equipment_id": "equipment uuid",
            "availability_score": 3,
            "fiability_score": 2,
            "process_safety_score": 4
        }
        // ... more training records (max 1000)
    ]
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "message": "Please send training data in request body"
            }), 400
        
        print(f"🎯 Received training request with {len(data) if isinstance(data, list) else 1} records")
        
        # Ensure data is a list
        if not isinstance(data, list):
            data = [data]
        
        # Start training process
        result = training_manager.train_with_new_data(data)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ Training endpoint error: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Training failed",
            "message": str(e),
            "success": False
        }), 500

@app.route('/train/status', methods=['GET'])
def training_status():
    """Get current training status and history"""
    try:
        status = training_manager.get_training_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "error": "Failed to get training status",
            "message": str(e)
        }), 500

@app.route('/train/reload', methods=['POST'])
def reload_models():
    """
    Reload models after training to use the updated versions
    This is useful after training to refresh the prediction API
    """
    try:
        global predictor
        
        print("🔄 Reloading models after training...")
        success = initialize_models()
        
        if success:
            return jsonify({
                "success": True,
                "message": "Models reloaded successfully",
                "models_loaded": predictor is not None
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to reload models",
                "models_loaded": False
            }), 500
            
    except Exception as e:
        print(f"❌ Model reload error: {e}")
        return jsonify({
            "error": "Model reload failed",
            "message": str(e),
            "success": False
        }), 500

@app.route('/train/backups', methods=['GET'])
def list_backups():
    """List available model backups"""
    try:
        import os
        backup_dir = training_manager.backup_dir
        
        if not os.path.exists(backup_dir):
            return jsonify({
                "backups": [],
                "count": 0
            }), 200
        
        backups = []
        for item in os.listdir(backup_dir):
            backup_path = os.path.join(backup_dir, item)
            if os.path.isdir(backup_path) and item.startswith('backup_'):
                # Parse timestamp from backup name
                timestamp_str = item.replace('backup_', '')
                try:
                    from datetime import datetime
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                    formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = timestamp_str
                
                backups.append({
                    "name": item,
                    "created": formatted_time,
                    "path": backup_path
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['name'], reverse=True)
        
        return jsonify({
            "backups": backups,
            "count": len(backups)
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to list backups",
            "message": str(e)
        }), 500

@app.route('/train/restore/<backup_name>', methods=['POST'])
def restore_backup(backup_name):
    """Restore models from a specific backup"""
    try:
        result = training_manager.restore_backup(backup_name)
        
        if result["success"]:
            # Reload models after restore
            global predictor
            initialize_models()
            
            return jsonify({
                **result,
                "models_reloaded": True
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "error": "Backup restore failed",
            "message": str(e),
            "success": False
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "message": "Available endpoints: /health, /predict, /models/info"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed",
        "message": "Check the HTTP method for this endpoint"
    }), 405

# Initialize models when module loads (for production deployment)
print("🚀 Starting Equipment Prediction API...")
print("🔄 Initializing ML models...")
initialize_models()

if __name__ == '__main__':
    # Development server only
    print("🌐 Starting development server...")
    print("📡 API Endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /models/info - Model information") 
    print("  GET  /models/metrics - Model performance metrics")
    print("  POST /predict - Make predictions (single or batch)")
    print("  POST /train - Train models with new data")
    print("  GET  /train/status - Training status")
    print("  POST /train/reload - Reload models")
    print("  GET  /train/backups - List backups")
    print("  POST /train/restore/<backup> - Restore backup")
    app.run(host='0.0.0.0', port=5000, debug=True) 