__author__ = 'Anna'

from sqlalchemy import String
from geoalchemy2 import Geometry
from SetBaseTaxAndPrice import *


class SetTaxAndPriceZone(Base):

    __tablename__ = 'set_tax_and_price_zone'

    fid = Column(Integer, Sequence('set_tax_and_price_zone_fid_seq'), primary_key=True)
    location = Column(String)
    zone_no = Column(Integer)
    area_m2 = Column(Numeric)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    taxes = relationship("SetBaseTaxAndPrice", backref='parent', cascade="all, delete, delete-orphan")
