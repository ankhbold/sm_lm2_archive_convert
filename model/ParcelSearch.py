__author__ = 'mwagner'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ClLanduseType import *
from Base import *


class ParcelSearch(Base):

    __tablename__ = 'parcel_search'

    parcel_id = Column(String, primary_key=True)
    old_parcel_id = Column(Integer)
    geo_id = Column(String)
    person_id = Column(String)
    person_pk_id = Column(Integer)
    name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    app_no = Column(String)
    decision_no = Column(String)
    contract_no = Column(String)
    record_no = Column(String)

    landuse = Column(Integer, ForeignKey('cl_landuse_type.code'))
    landuse_ref = relationship("ClLanduseType")
