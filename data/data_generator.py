import json
import random
from faker import Faker
import uuid
from datetime import datetime, timedelta

fake = Faker('en_IN') # Indian locale for realistic names and addresses

NUM_FIRS = 1000
NUM_SYNDICATES = 3
SYNDICATE_SIZE = 5 # 5 key members per syndicate

def generate_data():
    suspects = []
    firs = []
    
    # 1. Generate Syndicate Members (Organized Crime)
    syndicates = []
    for i in range(NUM_SYNDICATES):
        # A syndicate shares a few common phone numbers or vehicles to leave a graph footprint
        syndicate_phone = fake.phone_number()
        syndicate_vehicle = fake.license_plate()
        
        members = []
        for j in range(SYNDICATE_SIZE):
            member = {
                "id": str(uuid.uuid4()),
                "name": fake.name(),
                "age": random.randint(20, 50),
                "phone": syndicate_phone if random.random() > 0.5 else fake.phone_number(),
                "vehicle": syndicate_vehicle if random.random() > 0.5 else fake.license_plate(),
                "syndicate_id": f"SYN-{i}" # Hidden label to verify our ML models
            }
            members.append(member)
            suspects.append(member)
        syndicates.append(members)
        
    # 2. Generate Random Independent Suspects
    for _ in range(200):
        suspects.append({
            "id": str(uuid.uuid4()),
            "name": fake.name(),
            "age": random.randint(18, 65),
            "phone": fake.phone_number(),
            "vehicle": fake.license_plate(),
            "syndicate_id": None
        })
        
    # 3. Generate FIRs
    locations = [
        ("Indiranagar", 12.9719, 77.6412),
        ("Koramangala", 12.9279, 77.6271),
        ("Jayanagar", 12.9299, 77.5824),
        ("Whitefield", 12.9698, 77.7499),
        ("Malleswaram", 13.0031, 77.5700)
    ]
    
    crime_types = [
        ("Robbery", ["392", "397"], ["Weapon", "Night", "Two-wheeler"]),
        ("Chain Snatching", ["379", "356"], ["Bike-borne", "Early Morning", "Helmet"]),
        ("Burglary", ["457", "380"], ["Broken Lock", "Unattended House", "Crowbar"]),
        ("Assault", ["323", "324"], ["Argument", "Drunk", "Blunt Object"])
    ]

    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(NUM_FIRS):
        crime, sections, mo_tags = random.choice(crime_types)
        loc_name, lat, lng = random.choice(locations)
        
        # Add some noise to coordinates
        lat += random.uniform(-0.01, 0.01)
        lng += random.uniform(-0.01, 0.01)
        
        date = start_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
        
        # Decide if this crime is committed by a syndicate or random suspect
        if random.random() < 0.2:
            # Syndicate crime
            syndicate = random.choice(syndicates)
            involved_suspects = random.sample(syndicate, k=random.randint(1, 3))
        else:
            # Random crime
            involved_suspects = [random.choice(suspects)]
            
        fir = {
            "fir_id": f"FIR-2023-BLR-{i:05d}",
            "date": date.isoformat(),
            "location": {"name": loc_name, "lat": lat, "lng": lng},
            "type": crime,
            "ipc_sections": sections,
            "mo_tags": random.sample(mo_tags, k=2),
            "suspects_involved": [s["id"] for s in involved_suspects],
            "narrative": f"Incident occurred at {loc_name}. The suspect(s) used {random.choice(mo_tags)}."
        }
        firs.append(fir)
        
    with open("firs.json", "w") as f:
        json.dump(firs, f, indent=2)
        
    with open("suspects.json", "w") as f:
        json.dump(suspects, f, indent=2)
        
    print(f"Successfully generated {len(firs)} FIRs and {len(suspects)} Suspects.")

if __name__ == "__main__":
    generate_data()
