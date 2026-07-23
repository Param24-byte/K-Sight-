import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker
import uuid

# Add backend to path so we can import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from src.services.db.database import engine, SessionLocal, Base
# Import all models to ensure they are registered with Base metadata
from src.services.db.models import *

fake = Faker('en_IN')

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

def generate_data():
    reset_db()
    db = SessionLocal()
    
    print("Populating Lookups...")
    
    state = State(StateName="Karnataka", NationalityID=1)
    db.add(state)
    db.commit()
    
    districts = [District(DistrictName=name, StateID=state.StateID) for name in ["Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Hubballi"]]
    db.add_all(districts)
    db.commit()
    
    utypes = [UnitType(UnitTypeName="Police Station", CityDistState="City"), UnitType(UnitTypeName="Circle Office", CityDistState="City")]
    db.add_all(utypes)
    db.commit()
    
    ps_names = ["Indiranagar PS", "Koramangala PS", "Jayanagar PS", "Whitefield PS", "Malleswaram PS"]
    units = [Unit(UnitName=name, TypeID=utypes[0].UnitTypeID, StateID=state.StateID, DistrictID=districts[0].DistrictID) for name in ps_names]
    db.add_all(units)
    db.commit()

    ranks = [Rank(RankName=name, Hierarchy=i) for i, name in enumerate(["Constable", "Head Constable", "Sub-Inspector", "Inspector", "DSP"])]
    db.add_all(ranks)
    db.commit()
    
    designations = [Designation(DesignationName=name, SortOrder=i) for i, name in enumerate(["Investigating Officer", "Station House Officer"])]
    db.add_all(designations)
    db.commit()
    
    categories = [CaseCategory(LookupValue=name) for name in ["FIR", "UDR", "PAR"]]
    db.add_all(categories)
    db.commit()
    
    gravities = [GravityOffence(LookupValue=name) for name in ["Heinous", "Non-Heinous"]]
    db.add_all(gravities)
    db.commit()
    
    castes = [CasteMaster(caste_master_name=name) for name in ["General", "OBC", "SC/ST"]]
    db.add_all(castes)
    
    religions = [ReligionMaster(ReligionName=name) for name in ["Hindu", "Muslim", "Christian", "Other"]]
    db.add_all(religions)
    
    occupations = [OccupationMaster(OccupationName=name) for name in ["Private Employee", "Government Employee", "Business", "Student", "Unemployed"]]
    db.add_all(occupations)
    
    statuses = [CaseStatusMaster(CaseStatusName=name) for name in ["Under Investigation", "Charge Sheeted", "Closed", "Undetected"]]
    db.add_all(statuses)
    
    courts = [Court(CourtName=f"Fast Track Court {i}", DistrictID=districts[0].DistrictID, StateID=state.StateID) for i in range(1, 4)]
    db.add_all(courts)
    db.commit()

    acts = [
        Act(ActCode="IPC", ActDescription="Indian Penal Code", ShortName="IPC"),
        Act(ActCode="NDPS", ActDescription="Narcotics Drugs Act", ShortName="NDPS")
    ]
    db.add_all(acts)
    db.commit()
    
    sections = [
        Section(ActCode="IPC", SectionCode="392", SectionDescription="Robbery"),
        Section(ActCode="IPC", SectionCode="302", SectionDescription="Murder"),
        Section(ActCode="IPC", SectionCode="323", SectionDescription="Assault"),
        Section(ActCode="IPC", SectionCode="379", SectionDescription="Theft"),
        Section(ActCode="NDPS", SectionCode="20b", SectionDescription="Cannabis possession")
    ]
    db.add_all(sections)
    db.commit()
    
    cheads = [CrimeHead(CrimeGroupName="Crimes Against Body"), CrimeHead(CrimeGroupName="Crimes Against Property")]
    db.add_all(cheads)
    db.commit()
    
    csubheads = [
        CrimeSubHead(CrimeHeadID=cheads[0].CrimeHeadID, CrimeHeadName="Murder", SeqID=1),
        CrimeSubHead(CrimeHeadID=cheads[0].CrimeHeadID, CrimeHeadName="Assault", SeqID=2),
        CrimeSubHead(CrimeHeadID=cheads[1].CrimeHeadID, CrimeHeadName="Robbery", SeqID=3),
        CrimeSubHead(CrimeHeadID=cheads[1].CrimeHeadID, CrimeHeadName="Theft", SeqID=4)
    ]
    db.add_all(csubheads)
    db.commit()
    
    # Add Police Employees
    employees = []
    for u in units:
        for _ in range(5):
            emp = Employee(
                DistrictID=u.DistrictID,
                UnitID=u.UnitID,
                RankID=random.choice(ranks).RankID,
                DesignationID=random.choice(designations).DesignationID,
                KGID=f"KGID-{random.randint(10000, 99999)}",
                FirstName=fake.first_name(),
                EmployeeDOB=fake.date_of_birth(minimum_age=22, maximum_age=55),
                GenderID=random.choice([1, 2]),
                BloodGroupID=1,
                PhysicallyChallenged=False,
                AppointmentDate=fake.date_between(start_date='-10y', end_date='today')
            )
            employees.append(emp)
    db.add_all(employees)
    db.commit()

    print("Generating Cases...")
    
    locations = [
        (12.9719, 77.6412), # Indiranagar
        (12.9279, 77.6271), # Koramangala
        (12.9299, 77.5824), # Jayanagar
        (12.9698, 77.7499), # Whitefield
        (13.0031, 77.5700)  # Malleswaram
    ]
    
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(500):
        # Determine crime type
        csub = random.choice(csubheads)
        
        # Link section based on subhead loosely
        if csub.CrimeHeadName == "Robbery": sec = sections[0]
        elif csub.CrimeHeadName == "Murder": sec = sections[1]
        elif csub.CrimeHeadName == "Assault": sec = sections[2]
        else: sec = sections[3]
            
        unit = random.choice(units)
        emp = random.choice([e for e in employees if e.UnitID == unit.UnitID])
        
        lat, lng = locations[units.index(unit)]
        lat += random.uniform(-0.02, 0.02)
        lng += random.uniform(-0.02, 0.02)
        
        reg_date = fake.date_between(start_date='-1y', end_date='today')
        inc_date = datetime.combine(reg_date, datetime.min.time()) - timedelta(days=random.randint(0,5))
        
        case = CaseMaster(
            CrimeNo=f"1{districts[0].DistrictID:04d}{unit.UnitID:04d}2026{i:05d}",
            CaseNo=f"2026{i:05d}",
            CrimeRegisteredDate=reg_date,
            PolicePersonID=emp.EmployeeID,
            PoliceStationID=unit.UnitID,
            CaseCategoryID=categories[0].CaseCategoryID,
            GravityOffenceID=gravities[0].GravityOffenceID if sec.SectionCode in ["302", "392"] else gravities[1].GravityOffenceID,
            CrimeMajorHeadID=csub.CrimeHeadID,
            CrimeMinorHeadID=csub.CrimeSubHeadID,
            CaseStatusID=random.choice(statuses).CaseStatusID,
            CourtID=courts[0].CourtID,
            IncidentFromDate=inc_date,
            IncidentToDate=inc_date + timedelta(hours=random.randint(1, 4)),
            InfoReceivedPSDate=inc_date + timedelta(days=random.randint(0, 1)),
            latitude=lat,
            longitude=lng,
            BriefFacts=f"Incident of {csub.CrimeHeadName} reported near {unit.UnitName} jurisdiction."
        )
        db.add(case)
        db.commit() # commit to get ID
        
        # Complainant
        comp = ComplainantDetails(
            CaseMasterID=case.CaseMasterID,
            ComplainantName=fake.name(),
            AgeYear=random.randint(18, 70),
            OccupationID=random.choice(occupations).OccupationID,
            ReligionID=random.choice(religions).ReligionID,
            CasteID=random.choice(castes).caste_master_id,
            GenderID=random.choice([1, 2])
        )
        db.add(comp)
        
        # Act/Section
        assoc = ActSectionAssociation(
            CaseMasterID=case.CaseMasterID,
            ActID=sec.ActCode,
            SectionID=sec.id,
            ActOrderID=1,
            SectionOrderID=1
        )
        db.add(assoc)
        
        # Victim
        if random.random() > 0.3:
            vic = Victim(
                CaseMasterID=case.CaseMasterID,
                VictimName=fake.name(),
                AgeYear=random.randint(10, 80),
                GenderID=random.choice([1, 2]),
                VictimPolice="0"
            )
            db.add(vic)
            
        # Accused
        num_accused = random.randint(1, 3)
        for a_idx in range(num_accused):
            acc = Accused(
                CaseMasterID=case.CaseMasterID,
                AccusedName=fake.name(),
                AgeYear=random.randint(18, 55),
                GenderID=random.choice([1, 2]),
                PersonID=f"A{a_idx+1}"
            )
            db.add(acc)
            db.commit() # commit to get acc ID
            
            # Arrest
            if case.CaseStatusID != statuses[-1].CaseStatusID and random.random() > 0.5:
                arr = ArrestSurrender(
                    CaseMasterID=case.CaseMasterID,
                    ArrestSurrenderTypeID=1,
                    ArrestSurrenderDate=reg_date + timedelta(days=random.randint(1, 10)),
                    ArrestSurrenderStateId=state.StateID,
                    ArrestSurrenderDistrictId=districts[0].DistrictID,
                    PoliceStationID=unit.UnitID,
                    IOID=emp.EmployeeID,
                    CourtID=courts[0].CourtID,
                    AccusedMasterID=acc.AccusedMasterID,
                    IsAccused=True,
                    IsComplainantAccused=False
                )
                db.add(arr)
        
        db.commit()

    print("Data generation complete! Populated PostgreSQL with relational ER data.")
    db.close()

if __name__ == "__main__":
    generate_data()
