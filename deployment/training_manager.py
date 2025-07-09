import pandas as pd
import numpy as np
import pickle
import threading
import time
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid
from comprehensive_prediction_system import ComprehensiveEquipmentPredictor

class TrainingManager:
    """
    Manages incremental training of ML models with new anomaly data
    Handles data validation, CSV updates, model retraining, and versioning
    """
    
    def __init__(self):
        self.training_lock = threading.Lock()
        self.is_training = False
        self.predictor = None
        self.training_history = []
        
        # Data file paths
        self.data_files = {
            'availability': 'disponibilite.csv',
            'fiability': 'fiabilite.csv', 
            'process_safety': 'process_safty.csv'
        }
        
        # Model file paths
        self.model_files = {
            'availability': 'availability_model.pkl',
            'fiability': 'fiability_model.pkl',
            'process_safety': 'process_safety_model.pkl'
        }
        
        # Backup directory
        self.backup_dir = 'model_backups'
        os.makedirs(self.backup_dir, exist_ok=True)
        
        print("🎯 TrainingManager initialized")
    
    def validate_training_data(self, training_data: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate new training data format and content
        
        Args:
            training_data: List of anomaly records to train on
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        
        errors = []
        
        if not isinstance(training_data, list):
            errors.append("Training data must be a list")
            return False, errors
        
        if len(training_data) == 0:
            errors.append("Training data cannot be empty")
            return False, errors
        
        if len(training_data) > 1000:
            errors.append(f"Maximum 1000 training records allowed, got {len(training_data)}")
            return False, errors
        
        required_fields = [
            'anomaly_id', 'description', 'equipment_name', 'equipment_id',
            'availability_score', 'fiability_score', 'process_safety_score'
        ]
        
        for i, record in enumerate(training_data):
            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in record or record[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                errors.append(f"Record {i+1}: Missing required fields: {missing_fields}")
                continue
            
            # Validate data types and ranges
            try:
                # Validate scores (must be numeric 1-5)
                for score_field in ['availability_score', 'fiability_score', 'process_safety_score']:
                    score = float(record[score_field])
                    if not (1 <= score <= 5):
                        errors.append(f"Record {i+1}: {score_field} must be between 1 and 5, got {score}")
                
                # Validate string fields
                for str_field in ['anomaly_id', 'description', 'equipment_name', 'equipment_id']:
                    if not isinstance(record[str_field], str) or len(record[str_field].strip()) == 0:
                        errors.append(f"Record {i+1}: {str_field} must be a non-empty string")
                
                # Validate description length
                if len(record['description']) > 2000:
                    errors.append(f"Record {i+1}: Description too long (max 2000 characters)")
                
            except (ValueError, TypeError) as e:
                errors.append(f"Record {i+1}: Data type error - {str(e)}")
        
        return len(errors) == 0, errors
    
    def backup_models(self) -> str:
        """
        Create backup of current models before training
        
        Returns:
            Backup directory path
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Backup model files
        for model_type, model_file in self.model_files.items():
            if os.path.exists(model_file):
                backup_file = os.path.join(backup_path, model_file)
                shutil.copy2(model_file, backup_file)
                print(f"📦 Backed up {model_file} to {backup_file}")
        
        # Backup CSV files
        for data_type, data_file in self.data_files.items():
            if os.path.exists(data_file):
                backup_file = os.path.join(backup_path, data_file)
                shutil.copy2(data_file, backup_file)
                print(f"📦 Backed up {data_file} to {backup_file}")
        
        return backup_path
    
    def update_csv_files(self, training_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Update CSV files with new training data
        
        Args:
            training_data: Validated training data
            
        Returns:
            Dictionary with number of records added to each file
        """
        
        records_added = {'availability': 0, 'fiability': 0, 'process_safety': 0}
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for data_type, csv_file in self.data_files.items():
            # Prepare new records for this data type
            new_records = []
            
            for record in training_data:
                # Map the score field name
                score_field_map = {
                    'availability': 'availability_score',
                    'fiability': 'fiability_score', 
                    'process_safety': 'process_safety_score'
                }
                
                target_column_map = {
                    'availability': 'Disponibilté',
                    'fiability': 'Fiabilité Intégrité',
                    'process_safety': 'Process Safety'
                }
                
                # Create CSV record
                csv_record = {
                    'Num_equipement': record['equipment_id'],
                    'Systeme': str(uuid.uuid4()),  # Generate system ID
                    'Description': record['description'],
                    'Date de détéction de l\'anomalie': current_time,
                    'Description de l\'équipement': record['equipment_name'],
                    'Section propriétaire': 'TRAIN',  # Mark as training data
                    target_column_map[data_type]: record[score_field_map[data_type]]
                }
                
                new_records.append(csv_record)
            
            # Load existing CSV and append new records
            if os.path.exists(csv_file):
                existing_df = pd.read_csv(csv_file)
                new_df = pd.DataFrame(new_records)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = pd.DataFrame(new_records)
            
            # Save updated CSV
            combined_df.to_csv(csv_file, index=False)
            records_added[data_type] = len(new_records)
            print(f"📝 Added {len(new_records)} records to {csv_file}")
        
        return records_added
    
    def retrain_models(self) -> Dict[str, bool]:
        """
        Retrain all three models with updated data
        
        Returns:
            Dictionary indicating success/failure for each model
        """
        
        training_results = {'availability': False, 'fiability': False, 'process_safety': False}
        
        try:
            # Initialize fresh predictor
            self.predictor = ComprehensiveEquipmentPredictor()
            
            # Train availability model
            print("🔄 Retraining availability model...")
            self.predictor.availability_predictor.load_historical_data()
            X_avail, y_avail = self.predictor.availability_predictor.prepare_training_data()
            self.predictor.availability_predictor.train_model(X_avail, y_avail)
            self.predictor.availability_predictor.save_model()
            training_results['availability'] = True
            print("✅ Availability model retrained")
            
            # Train fiability model
            print("🔄 Retraining fiability model...")
            self.predictor.fiability_predictor.load_historical_data()
            X_fiab, y_fiab = self.predictor.fiability_predictor.prepare_training_data()
            self.predictor.fiability_predictor.train_model(X_fiab, y_fiab)
            self.predictor.fiability_predictor.save_model()
            training_results['fiability'] = True
            print("✅ Fiability model retrained")
            
            # Train process safety model
            print("🔄 Retraining process safety model...")
            self.predictor.process_safety_predictor.load_historical_data()
            X_safety, y_safety = self.predictor.process_safety_predictor.prepare_training_data()
            self.predictor.process_safety_predictor.train_model(X_safety, y_safety)
            self.predictor.process_safety_predictor.save_model()
            training_results['process_safety'] = True
            print("✅ Process safety model retrained")
            
        except Exception as e:
            print(f"❌ Error during model retraining: {e}")
            import traceback
            traceback.print_exc()
        
        return training_results
    
    def train_with_new_data(self, training_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main method to train models with new anomaly data
        
        Args:
            training_data: List of new anomaly records
            
        Returns:
            Training results and statistics
        """
        
        # Acquire training lock to prevent concurrent training
        if not self.training_lock.acquire(blocking=False):
            return {
                "success": False,
                "error": "Training already in progress. Please wait and try again.",
                "is_training": True
            }
        
        try:
            self.is_training = True
            training_start_time = time.time()
            
            print(f"🚀 Starting incremental training with {len(training_data)} new records...")
            
            # Step 1: Validate data
            print("🔍 Validating training data...")
            is_valid, validation_errors = self.validate_training_data(training_data)
            
            if not is_valid:
                return {
                    "success": False,
                    "error": "Data validation failed",
                    "validation_errors": validation_errors,
                    "is_training": False
                }
            
            print("✅ Data validation passed")
            
            # Step 2: Backup current models
            print("📦 Creating model backups...")
            backup_path = self.backup_models()
            
            # Step 3: Update CSV files
            print("📝 Updating training data files...")
            records_added = self.update_csv_files(training_data)
            
            # Step 4: Retrain models
            print("🎯 Retraining models...")
            training_results = self.retrain_models()
            
            # Step 5: Calculate training statistics
            training_time = time.time() - training_start_time
            
            # Record training session
            training_session = {
                "timestamp": datetime.now().isoformat(),
                "records_added": sum(records_added.values()),
                "training_time": round(training_time, 2),
                "models_retrained": sum(training_results.values()),
                "backup_path": backup_path,
                "success": all(training_results.values())
            }
            
            self.training_history.append(training_session)
            
            print(f"🎉 Training completed in {training_time:.2f} seconds")
            
            return {
                "success": all(training_results.values()),
                "message": "Incremental training completed successfully",
                "statistics": {
                    "total_records_added": sum(records_added.values()),
                    "records_per_model": records_added,
                    "training_time_seconds": round(training_time, 2),
                    "models_retrained": training_results,
                    "backup_location": backup_path
                },
                "training_session_id": len(self.training_history),
                "is_training": False
            }
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": f"Training failed: {str(e)}",
                "is_training": False
            }
        
        finally:
            self.is_training = False
            self.training_lock.release()
    
    def get_training_status(self) -> Dict[str, Any]:
        """
        Get current training status and history
        
        Returns:
            Training status information
        """
        
        return {
            "is_training": self.is_training,
            "training_sessions_completed": len(self.training_history),
            "last_training": self.training_history[-1] if self.training_history else None,
            "available_backups": len([f for f in os.listdir(self.backup_dir) 
                                    if f.startswith('backup_')]) if os.path.exists(self.backup_dir) else 0
        }
    
    def restore_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        Restore models from a backup
        
        Args:
            backup_name: Name of backup to restore
            
        Returns:
            Restore operation result
        """
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return {
                "success": False,
                "error": f"Backup {backup_name} not found"
            }
        
        try:
            # Restore model files
            for model_file in self.model_files.values():
                backup_file = os.path.join(backup_path, model_file)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, model_file)
                    print(f"🔄 Restored {model_file}")
            
            # Restore CSV files
            for data_file in self.data_files.values():
                backup_file = os.path.join(backup_path, data_file)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, data_file)
                    print(f"🔄 Restored {data_file}")
            
            return {
                "success": True,
                "message": f"Successfully restored from backup {backup_name}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to restore backup: {str(e)}"
            }

# Global training manager instance
training_manager = TrainingManager() 