from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.services.db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String) # Investigator, Analyst, Supervisor, Policymaker

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    action = Column(String)
    endpoint = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ================= Lookup & Master Tables =================

class State(Base):
    __tablename__ = "State"
    StateID = Column(Integer, primary_key=True, index=True)
    StateName = Column(String)
    NationalityID = Column(Integer)
    Active = Column(Boolean, default=True)

class District(Base):
    __tablename__ = "District"
    DistrictID = Column(Integer, primary_key=True, index=True)
    DistrictName = Column(String)
    StateID = Column(Integer, ForeignKey("State.StateID"))
    Active = Column(Boolean, default=True)

class UnitType(Base):
    __tablename__ = "UnitType"
    UnitTypeID = Column(Integer, primary_key=True, index=True)
    UnitTypeName = Column(String)
    CityDistState = Column(String)

class Unit(Base):
    __tablename__ = "Unit"
    UnitID = Column(Integer, primary_key=True, index=True)
    UnitName = Column(String)
    TypeID = Column(Integer, ForeignKey("UnitType.UnitTypeID"))
    ParentUnit = Column(Integer)
    NationalityID = Column(Integer)
    StateID = Column(Integer, ForeignKey("State.StateID"))
    DistrictID = Column(Integer, ForeignKey("District.DistrictID"))
    Active = Column(Boolean, default=True)

class Rank(Base):
    __tablename__ = "Rank"
    RankID = Column(Integer, primary_key=True, index=True)
    RankName = Column(String)
    Hierarchy = Column(Integer)
    Active = Column(Boolean, default=True)

class Designation(Base):
    __tablename__ = "Designation"
    DesignationID = Column(Integer, primary_key=True, index=True)
    DesignationName = Column(String)
    Active = Column(Boolean, default=True)
    SortOrder = Column(Integer)

class CaseCategory(Base):
    __tablename__ = "CaseCategory"
    CaseCategoryID = Column(Integer, primary_key=True, index=True)
    LookupValue = Column(String)

class GravityOffence(Base):
    __tablename__ = "GravityOffence"
    GravityOffenceID = Column(Integer, primary_key=True, index=True)
    LookupValue = Column(String)

class CasteMaster(Base):
    __tablename__ = "CasteMaster"
    caste_master_id = Column(Integer, primary_key=True, index=True)
    caste_master_name = Column(String)

class ReligionMaster(Base):
    __tablename__ = "ReligionMaster"
    ReligionID = Column(Integer, primary_key=True, index=True)
    ReligionName = Column(String)

class OccupationMaster(Base):
    __tablename__ = "OccupationMaster"
    OccupationID = Column(Integer, primary_key=True, index=True)
    OccupationName = Column(String)

class CaseStatusMaster(Base):
    __tablename__ = "CaseStatusMaster"
    CaseStatusID = Column(Integer, primary_key=True, index=True)
    CaseStatusName = Column(String)

class Court(Base):
    __tablename__ = "Court"
    CourtID = Column(Integer, primary_key=True, index=True)
    CourtName = Column(String)
    DistrictID = Column(Integer, ForeignKey("District.DistrictID"))
    StateID = Column(Integer, ForeignKey("State.StateID"))
    Active = Column(Boolean, default=True)

class Act(Base):
    __tablename__ = "Act"
    ActCode = Column(String, primary_key=True, index=True)
    ActDescription = Column(String)
    ShortName = Column(String)
    Active = Column(Boolean, default=True)

class Section(Base):
    __tablename__ = "Section"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ActCode = Column(String, ForeignKey("Act.ActCode"))
    SectionCode = Column(String)
    SectionDescription = Column(String)
    Active = Column(Boolean, default=True)

class CrimeHead(Base):
    __tablename__ = "CrimeHead"
    CrimeHeadID = Column(Integer, primary_key=True, index=True)
    CrimeGroupName = Column(String)
    Active = Column(Boolean, default=True)

class CrimeSubHead(Base):
    __tablename__ = "CrimeSubHead"
    CrimeSubHeadID = Column(Integer, primary_key=True, index=True)
    CrimeHeadID = Column(Integer, ForeignKey("CrimeHead.CrimeHeadID"))
    CrimeHeadName = Column(String)
    SeqID = Column(Integer)

# ================= People / Employees =================

class Employee(Base):
    __tablename__ = "Employee"
    EmployeeID = Column(Integer, primary_key=True, index=True)
    DistrictID = Column(Integer, ForeignKey("District.DistrictID"))
    UnitID = Column(Integer, ForeignKey("Unit.UnitID"))
    RankID = Column(Integer, ForeignKey("Rank.RankID"))
    DesignationID = Column(Integer, ForeignKey("Designation.DesignationID"))
    KGID = Column(String)
    FirstName = Column(String)
    EmployeeDOB = Column(Date)
    GenderID = Column(Integer)
    BloodGroupID = Column(Integer)
    PhysicallyChallenged = Column(Boolean)
    AppointmentDate = Column(Date)

# ================= Core Case Tables =================

class CaseMaster(Base):
    __tablename__ = "CaseMaster"
    CaseMasterID = Column(Integer, primary_key=True, index=True)
    CrimeNo = Column(String, index=True)
    CaseNo = Column(String, index=True)
    CrimeRegisteredDate = Column(Date)
    PolicePersonID = Column(Integer, ForeignKey("Employee.EmployeeID"))
    PoliceStationID = Column(Integer, ForeignKey("Unit.UnitID"))
    CaseCategoryID = Column(Integer, ForeignKey("CaseCategory.CaseCategoryID"))
    GravityOffenceID = Column(Integer, ForeignKey("GravityOffence.GravityOffenceID"))
    CrimeMajorHeadID = Column(Integer, ForeignKey("CrimeHead.CrimeHeadID"))
    CrimeMinorHeadID = Column(Integer, ForeignKey("CrimeSubHead.CrimeSubHeadID"))
    CaseStatusID = Column(Integer, ForeignKey("CaseStatusMaster.CaseStatusID"))
    CourtID = Column(Integer, ForeignKey("Court.CourtID"))
    
    IncidentFromDate = Column(DateTime)
    IncidentToDate = Column(DateTime)
    InfoReceivedPSDate = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    BriefFacts = Column(Text)

class ComplainantDetails(Base):
    __tablename__ = "ComplainantDetails"
    ComplainantID = Column(Integer, primary_key=True, index=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"))
    ComplainantName = Column(String)
    AgeYear = Column(Integer)
    OccupationID = Column(Integer, ForeignKey("OccupationMaster.OccupationID"))
    ReligionID = Column(Integer, ForeignKey("ReligionMaster.ReligionID"))
    CasteID = Column(Integer, ForeignKey("CasteMaster.caste_master_id"))
    GenderID = Column(Integer)

class ActSectionAssociation(Base):
    __tablename__ = "ActSectionAssociation"
    id = Column(Integer, primary_key=True, autoincrement=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"))
    ActID = Column(String, ForeignKey("Act.ActCode"))
    SectionID = Column(Integer, ForeignKey("Section.id"))
    ActOrderID = Column(Integer)
    SectionOrderID = Column(Integer)

class Victim(Base):
    __tablename__ = "Victim"
    VictimMasterID = Column(Integer, primary_key=True, index=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"))
    VictimName = Column(String)
    AgeYear = Column(Integer)
    GenderID = Column(Integer)
    VictimPolice = Column(String)

class Accused(Base):
    __tablename__ = "Accused"
    AccusedMasterID = Column(Integer, primary_key=True, index=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"))
    AccusedName = Column(String)
    AgeYear = Column(Integer)
    GenderID = Column(Integer)
    PersonID = Column(String)

class ArrestSurrender(Base):
    __tablename__ = "ArrestSurrender"
    ArrestSurrenderID = Column(Integer, primary_key=True, index=True)
    CaseMasterID = Column(Integer, ForeignKey("CaseMaster.CaseMasterID"))
    ArrestSurrenderTypeID = Column(Integer)
    ArrestSurrenderDate = Column(Date)
    ArrestSurrenderStateId = Column(Integer, ForeignKey("State.StateID"))
    ArrestSurrenderDistrictId = Column(Integer, ForeignKey("District.DistrictID"))
    PoliceStationID = Column(Integer, ForeignKey("Unit.UnitID"))
    IOID = Column(Integer, ForeignKey("Employee.EmployeeID"))
    CourtID = Column(Integer, ForeignKey("Court.CourtID"))
    AccusedMasterID = Column(Integer, ForeignKey("Accused.AccusedMasterID"))
    IsAccused = Column(Boolean)
    IsComplainantAccused = Column(Boolean)
