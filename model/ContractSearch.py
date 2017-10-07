__author__ = 'anna'

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from Base import *
from ClApplicationType import *
from ClApplicationStatus import *
from SetRole import *


class ContractSearch(Base):

    __tablename__ = 'contract_search'

    contract_no = Column(Integer, primary_key=True)
    contract_date = Column(Date)
    person_id = Column(String)
    person_pk_id = Column(Integer)
    name = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    parcel_id = Column(String)
    app_no = Column(String)
    decision_no = Column(String)