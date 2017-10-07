__author__ = 'mwagner'

from sqlalchemy import Column, Integer, String
from Base import *


class SetCertificate(Base):

    __tablename__ = 'set_certificate'

    type = Column(Integer, primary_key=True)
    description = Column(String)
    range_first_no = Column(Integer)
    range_last_no = Column(Integer)
    current_no = Column(Integer)
