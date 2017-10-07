__author__ = 'Anna'

from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from Base import *


class SetRole(Base):

    __tablename__ = 'set_role'

    user_name = Column(String, primary_key=True)
    surname = Column(String)
    first_name = Column(String)
    phone = Column(String)
    mac_addresses = Column(String)
    restriction_au_level1 = Column(String)
    restriction_au_level2 = Column(String)
    restriction_au_level3 = Column(String)
    pa_from = Column(Date)
    pa_till = Column(Date)

    # foreign keys:
    position = Column(Integer, ForeignKey('cl_position_type.code'))
    position_ref = relationship("ClPositionType")

    working_au_level1 = Column(String, ForeignKey('au_level1.code'))
    working_au_level1_ref = relationship("AuLevel1")

    working_au_level2 = Column(String, ForeignKey('au_level2.code'))
    working_au_level2_ref = relationship("AuLevel2")

    def __init__(self, user_name=None, surname=None, first_name=None, position=None, phone=None, mac_addresses=None,
                 restriction_au_level1=None, restriction_au_level2=None, restriction_au_level3=None, pa_from=None,
                 pa_till=None):

        self.user_name = user_name
        self.surname = surname
        self.first_name = first_name
        self.position = position
        self.phone = phone
        self.mac_addresses = mac_addresses
        self.restriction_au_level1 = restriction_au_level1
        self.restriction_au_level2 = restriction_au_level2
        self.restriction_au_level3 = restriction_au_level3
        self.pa_from = pa_from
        self.pa_till = pa_till
