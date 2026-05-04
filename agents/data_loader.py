"""
Data Loader Agent
Loads clinical data from CSV files and prepares it for analysis
"""

import pandas as pd
import os
from datetime import datetime

class DataLoaderAgent:
    """
    Agent responsible for loading and validating clinical data
    """
    
    def __init__(self, data_path='data/sample_data'):
        """
        Initialize with path to data directory
        """
        self.data_path = data_path
        self.patients = None
        self.readmissions = None
        self.infections = None
        self.claims = None
        self.appointments = None
        self.surveys = None
        
    def load_all_data(self):
        """
        Load all clinical datasets from CSV files
        Returns dict with all dataframes
        """
        print("📂 Data Loader Agent: Loading clinical data...\n")
        
        try:
            # Load patients
            print("  📋 Loading patients...")
            self.patients = pd.read_csv(f'{self.data_path}/patients.csv')
            self.patients['admission_date'] = pd.to_datetime(self.patients['admission_date'])
            self.patients['discharge_date'] = pd.to_datetime(self.patients['discharge_date'])
            print(f"     ✅ Loaded {len(self.patients):,} patient records")
            
            # Load readmissions
            print("  🔄 Loading readmissions...")
            self.readmissions = pd.read_csv(f'{self.data_path}/readmissions.csv')
            self.readmissions['original_discharge'] = pd.to_datetime(self.readmissions['original_discharge'])
            self.readmissions['readmission_date'] = pd.to_datetime(self.readmissions['readmission_date'])
            print(f"     ✅ Loaded {len(self.readmissions):,} readmission records")
            
            # Load infections
            print("  🦠 Loading infections...")
            self.infections = pd.read_csv(f'{self.data_path}/infections.csv')
            self.infections['onset_date'] = pd.to_datetime(self.infections['onset_date'])
            print(f"     ✅ Loaded {len(self.infections):,} infection records")
            
            # Load claims
            print("  💰 Loading claims...")
            self.claims = pd.read_csv(f'{self.data_path}/claims.csv')
            self.claims['submission_date'] = pd.to_datetime(self.claims['submission_date'])
            self.claims['payment_date'] = pd.to_datetime(self.claims['payment_date'])
            print(f"     ✅ Loaded {len(self.claims):,} claim records")
            
            # Load appointments
            print("  📅 Loading appointments...")
            self.appointments = pd.read_csv(f'{self.data_path}/appointments.csv')
            self.appointments['scheduled_time'] = pd.to_datetime(self.appointments['scheduled_time'])
            print(f"     ✅ Loaded {len(self.appointments):,} appointment records")
            
            # Load surveys
            print("  📊 Loading surveys...")
            self.surveys = pd.read_csv(f'{self.data_path}/surveys.csv')
            self.surveys['survey_date'] = pd.to_datetime(self.surveys['survey_date'])
            print(f"     ✅ Loaded {len(self.surveys):,} survey records")
            
            print("\n✅ All data loaded successfully!\n")
            
            return {
                'patients': self.patients,
                'readmissions': self.readmissions,
                'infections': self.infections,
                'claims': self.claims,
                'appointments': self.appointments,
                'surveys': self.surveys
            }
            
        except FileNotFoundError as e:
            print(f"❌ Error: Data file not found - {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return None
    
    def get_data_summary(self):
        """
        Get summary statistics of loaded data
        """
        if self.patients is None:
            print("⚠️  No data loaded yet. Call load_all_data() first.")
            return None
        
        summary = {
            'total_patients': len(self.patients),
            'total_readmissions': len(self.readmissions),
            'total_infections': len(self.infections),
            'total_claims': len(self.claims),
            'total_appointments': len(self.appointments),
            'total_surveys': len(self.surveys),
            'date_range': {
                'start': self.patients['admission_date'].min(),
                'end': self.patients['discharge_date'].max()
            },
            'departments': self.patients['department'].unique().tolist()
        }
        
        return summary
    
    def validate_data_quality(self):
        """
        Check data quality and completeness
        """
        print("🔍 Validating data quality...\n")
        
        issues = []
        
        # Check for missing values
        for name, df in [
            ('patients', self.patients),
            ('readmissions', self.readmissions),
            ('infections', self.infections),
            ('claims', self.claims),
            ('appointments', self.appointments),
            ('surveys', self.surveys)
        ]:
            missing = df.isnull().sum()
            if missing.any():
                issues.append(f"  ⚠️  {name}: {missing.sum()} missing values")
        
        # Check date ranges
        if self.patients['discharge_date'].min() < self.patients['admission_date'].min():
            issues.append("  ⚠️  Invalid dates: Some discharges before admissions")
        
        if len(issues) == 0:
            print("  ✅ Data quality: EXCELLENT\n")
            return True
        else:
            print("  ⚠️  Data quality issues found:")
            for issue in issues:
                print(issue)
            print()
            return False


# Test the agent
if __name__ == "__main__":
    print("="*60)
    print("TESTING DATA LOADER AGENT")
    print("="*60 + "\n")
    
    # Create agent
    loader = DataLoaderAgent()
    
    # Load all data
    data = loader.load_all_data()
    
    if data:
        # Show summary
        print("="*60)
        print("DATA SUMMARY")
        print("="*60)
        summary = loader.get_data_summary()
        print(f"\n📊 Total Records:")
        print(f"   Patients:     {summary['total_patients']:,}")
        print(f"   Readmissions: {summary['total_readmissions']:,}")
        print(f"   Infections:   {summary['total_infections']:,}")
        print(f"   Claims:       {summary['total_claims']:,}")
        print(f"   Appointments: {summary['total_appointments']:,}")
        print(f"   Surveys:      {summary['total_surveys']:,}")
        
        print(f"\n📅 Date Range:")
        print(f"   From: {summary['date_range']['start'].strftime('%Y-%m-%d')}")
        print(f"   To:   {summary['date_range']['end'].strftime('%Y-%m-%d')}")
        
        print(f"\n🏥 Departments: {', '.join(summary['departments'])}")
        
        # Validate quality
        print("\n" + "="*60)
        loader.validate_data_quality()
        
        print("="*60)
        print("✅ DATA LOADER AGENT TEST COMPLETE!")
        print("="*60)