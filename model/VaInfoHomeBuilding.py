__author__ = 'ankhbold'

from sqlalchemy import Column, Integer, String, Date, Sequence, ForeignKey, DateTime
from CaParcel import *

class VaInfoHomeBuilding(Base):

    __tablename__ = 'va_info_building'

    id = Column(Integer, primary_key=True)
    building_id = Column(String)
    area_m2 = Column(Float)
    floor = Column(Integer)
    status_year = Column(DateTime)
    construction_year = Column(DateTime)

    #foreign keys:
    register_no = Column(String, ForeignKey('va_info_parcel.register_no'))
    register_no_ref = relationship("VaInfoHomeParcel")

    landuse_building = Column(Integer, ForeignKey('cl_type_landuse_building.code'))
    landuse_building_ref = relationship("VaTypeLanduseBuilding")

    stove_type = Column(Integer, ForeignKey('cl_type_stove.code'))
    stove_type_ref = relationship("VaTypeStove")

    material_type = Column(Integer, ForeignKey('cl_type_material.code'))
    material_type_ref = relationship("VaTypeMaterial")

    heat_type = Column(Integer, ForeignKey('cl_type_heat.code'))
    heat_type_ref = relationship("VaTypeHeat")

    building_status = Column(Integer, ForeignKey('cl_type_status_building.code'))
    building_status_ref = relationship("VaTypeStatusBuilding")
