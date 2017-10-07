__author__ = 'Anna'

from sqlalchemy import String
from geoalchemy2 import Geometry
from SetBaseFee import *


class SetFeeZone(Base):

    __tablename__ = 'set_fee_zone'

    fid = Column(Integer, Sequence('set_fee_zone_fid_seq'), primary_key=True)
    location = Column(String)
    zone_no = Column(Integer)
    area_m2 = Column(Numeric)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    fees = relationship("SetBaseFee", backref='parent', cascade="all, delete, delete-orphan")
