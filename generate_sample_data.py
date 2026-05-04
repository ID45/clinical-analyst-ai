"""
Generate realistic sample clinical data for testing
This creates fake hospital data that looks like real patient records
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

print("🏥 Generating Sample Clinical Data...\n")

# Configuration
NUM_PATIENTS = 1000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 3, 31)  # Q1 2024

def generate_patients(n=NUM_PATIENTS):
    """
    Creates fake patient admission records
    Each patient gets: ID, age, diagnosis, admission/discharge dates, etc.
    """
    print(f"📋 Creating {n} patient records...")
    
    patients = []
    
    for i in range(n):
        # Random admission date in Q1 2024
        admission_date = START_DATE + timedelta(
            days=random.randint(0, 90)
        )
        
        # Realistic length of stay (gamma distribution matches real hospital data)
        los = max(1, int(np.random.gamma(shape=2, scale=2)))
        discharge_date = admission_date + timedelta(days=los)
        
        patient = {
            'patient_id': f'PT{i:05d}',
            'age': random.randint(18, 95),
            'gender': random.choice(['M', 'F']),
            'admission_date': admission_date,
            'discharge_date': discharge_date,
            'length_of_stay': los,
            'diagnosis': random.choice([
                'Pneumonia', 'Heart Failure', 'Diabetes Complications', 
                'Stroke', 'COPD', 'Sepsis', 'Hip Fracture',
                'Kidney Disease', 'Cancer Treatment', 'Surgical Procedure'
            ]),
            'discharge_status': random.choices(
                ['home', 'transferred', 'deceased'],
                weights=[0.92, 0.06, 0.02]
            )[0],
            'department': random.choice([
                'Cardiology', 'Pulmonology', 'General Medicine',
                'ICU', 'Emergency', 'Surgery', 'Nephrology'
            ])
        }
        
        patients.append(patient)
    
    df = pd.DataFrame(patients)
    print(f"   ✅ Created {len(df)} patient records")
    return df

def generate_readmissions(patients_df):
    """
    Simulates patients who come back within 30 days (quality metric)
    About 15% realistic readmission rate
    """
    print("🔄 Generating readmission events...")
    
    readmissions = []
    
    for _, patient in patients_df.iterrows():
        # 15% chance of readmission (realistic rate)
        if random.random() < 0.15:
            days_until = random.randint(1, 30)
            readmit_date = patient['discharge_date'] + timedelta(days=days_until)
            
            readmissions.append({
                'patient_id': patient['patient_id'],
                'original_discharge': patient['discharge_date'],
                'readmission_date': readmit_date,
                'days_between': days_until,
                'reason': random.choice([
                    'Same condition worsened',
                    'Complication from treatment',
                    'Medication issue',
                    'Unrelated new condition'
                ])
            })
    
    df = pd.DataFrame(readmissions)
    print(f"   ✅ Created {len(df)} readmission records")
    return df

def generate_infections(patients_df):
    """
    Creates healthcare-associated infection (HAI) records
    Low rate (~1%) as it should be in real hospitals
    """
    print("🦠 Generating infection records...")
    
    infections = []
    
    for _, patient in patients_df.iterrows():
        # Only patients staying 2+ days can get HAIs
        if patient['length_of_stay'] >= 2:
            # Small chance of HAI per patient day
            if random.random() < 0.01 * patient['length_of_stay']:
                infections.append({
                    'patient_id': patient['patient_id'],
                    'infection_type': random.choice([
                        'CLABSI',  # Central line infection
                        'CAUTI',   # Catheter infection
                        'SSI',     # Surgical site infection
                        'VAP',     # Ventilator pneumonia
                        'CDI'      # C. diff infection
                    ]),
                    'onset_date': patient['admission_date'] + timedelta(
                        days=random.randint(2, patient['length_of_stay'])
                    ),
                    'department': patient['department']
                })
    
    df = pd.DataFrame(infections)
    print(f"   ✅ Created {len(df)} infection records")
    return df

def generate_claims(patients_df):
    """
    Creates billing/insurance claim records
    Includes denials, payments, etc. for financial metrics
    """
    print("💰 Generating billing claims...")
    
    claims = []
    
    for _, patient in patients_df.iterrows():
        # Claim amount based on length of stay
        base_amount = 5000 + (patient['length_of_stay'] * 1500)
        claim_amount = base_amount + random.randint(-1000, 3000)
        
        claim = {
            'claim_id': f'CLM{len(claims):06d}',
            'patient_id': patient['patient_id'],
            'submission_date': patient['discharge_date'] + timedelta(days=2),
            'claim_amount': claim_amount,
            'allowed_amount': claim_amount * random.uniform(0.75, 0.95),
            'claim_status': random.choices(
                ['paid', 'denied', 'pending'],
                weights=[0.85, 0.10, 0.05]
            )[0],
            'payer': random.choice([
                'Medicare', 'Medicaid', 'BlueCross BlueShield', 
                'Aetna', 'UnitedHealthcare', 'Cigna'
            ]),
            'denial_reason': None,
            'paid_amount': 0,
            'payment_date': None
        }
        
        # Set payment details based on status
        if claim['claim_status'] == 'paid':
            claim['paid_amount'] = claim['allowed_amount'] * random.uniform(0.92, 1.0)
            claim['payment_date'] = claim['submission_date'] + timedelta(
                days=random.randint(30, 60)
            )
        elif claim['claim_status'] == 'denied':
            claim['denial_reason'] = random.choice([
                'Missing documentation',
                'Not medically necessary',
                'Coding error',
                'Duplicate claim',
                'Authorization not obtained'
            ])
        
        claims.append(claim)
    
    df = pd.DataFrame(claims)
    print(f"   ✅ Created {len(df)} claim records")
    return df

def generate_appointments(n=500):
    """
    Creates outpatient appointment records
    Used for no-show rate and wait time metrics
    """
    print("📅 Generating appointment records...")
    
    appointments = []
    
    for i in range(n):
        appt_date = START_DATE + timedelta(days=random.randint(0, 90))
        scheduled_time = appt_date.replace(
            hour=random.randint(8, 16),
            minute=random.choice([0, 15, 30, 45])
        )
        
        status = random.choices(
            ['completed', 'no_show', 'cancelled'],
            weights=[0.85, 0.10, 0.05]
        )[0]
        
        wait_time = None
        if status == 'completed':
            wait_time = random.randint(5, 60)  # minutes
        
        appointments.append({
            'appointment_id': f'APT{i:05d}',
            'patient_id': f'PT{random.randint(0, NUM_PATIENTS-1):05d}',
            'scheduled_time': scheduled_time,
            'status': status,
            'wait_time_minutes': wait_time,
            'department': random.choice([
                'Primary Care', 'Cardiology', 'Orthopedics',
                'Neurology', 'Dermatology'
            ])
        })
    
    df = pd.DataFrame(appointments)
    print(f"   ✅ Created {len(df)} appointment records")
    return df

def generate_surveys(patients_df, n=300):
    """
    Creates patient satisfaction survey responses (HCAHPS)
    Used for patient experience metrics
    """
    print("📊 Generating patient surveys...")
    
    surveys = []
    
    # Sample some patients who completed surveys
    survey_patients = patients_df.sample(n=min(n, len(patients_df)))
    
    for _, patient in survey_patients.iterrows():
        # Overall satisfaction (1-10 scale)
        overall = random.choices(
            range(1, 11),
            weights=[1, 1, 2, 3, 5, 8, 12, 15, 25, 28]  # Skewed toward higher scores
        )[0]
        
        surveys.append({
            'survey_id': f'SUR{len(surveys):05d}',
            'patient_id': patient['patient_id'],
            'survey_date': patient['discharge_date'] + timedelta(days=random.randint(3, 10)),
            'overall_satisfaction': overall,
            'staff_communication': random.randint(max(1, overall-2), min(10, overall+1)),
            'cleanliness': random.randint(max(1, overall-1), min(10, overall+1)),
            'pain_management': random.randint(max(1, overall-2), min(10, overall+1)),
            'would_recommend': random.choice(['Yes', 'No', 'Maybe']) if overall >= 7 else 'No'
        })
    
    df = pd.DataFrame(surveys)
    print(f"   ✅ Created {len(df)} survey responses")
    return df

# Generate all datasets
print("\n" + "="*50)
print("STARTING DATA GENERATION")
print("="*50 + "\n")

patients = generate_patients(NUM_PATIENTS)
readmissions = generate_readmissions(patients)
infections = generate_infections(patients)
claims = generate_claims(patients)
appointments = generate_appointments(500)
surveys = generate_surveys(patients, 300)

# Save to CSV
print("\n💾 Saving files to data/sample_data/...")
patients.to_csv('data/sample_data/patients.csv', index=False)
readmissions.to_csv('data/sample_data/readmissions.csv', index=False)
infections.to_csv('data/sample_data/infections.csv', index=False)
claims.to_csv('data/sample_data/claims.csv', index=False)
appointments.to_csv('data/sample_data/appointments.csv', index=False)
surveys.to_csv('data/sample_data/surveys.csv', index=False)

# Summary
print("\n" + "="*50)
print("✅ SAMPLE DATA GENERATION COMPLETE!")
print("="*50)
print(f"\nGenerated files:")
print(f"  📋 patients.csv        - {len(patients):,} records")
print(f"  🔄 readmissions.csv    - {len(readmissions):,} records")
print(f"  🦠 infections.csv      - {len(infections):,} records")
print(f"  💰 claims.csv          - {len(claims):,} records")
print(f"  📅 appointments.csv    - {len(appointments):,} records")
print(f"  📊 surveys.csv         - {len(surveys):,} records")
print(f"\n🎯 Ready to analyze!")