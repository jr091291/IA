from sqlalchemy import Column, String, Integer, Numeric
from base import Base

class Item(Base):
    # le decimos como se va a llamar nuestra tabla
    __tablename__ = "items"

    # declaramos la estructura
    id = Column(String, primary_key=True)
    title = Column(String)
    brank = Column(String)
    price = Column(Numeric)
    color = Column(String)
    opinions = Column(Integer)
    average_opinions = Column(Numeric)
    raw_description = Column(String)
    seller = Column(String)
    url = Column(String, unique=True)
    newspaper_uid = Column(String)
    n_tokens_title = Column(Integer)
    n_tokens_raw_description = Column(Integer)

    def __init__(self, uid,title,brank,price,color,opinions,average_opinions,raw_description,seller,url,newspaper_uid,n_tokens_title,n_tokens_raw_description):
        self.id = uid
        self.title = title
        self.brank = brank
        self.price = price
        self.color = color
        self.opinions = opinions
        self.average_opinions = average_opinions
        self.raw_description = raw_description
        self.seller = seller
        self.url = url
        self.newspaper_uid = newspaper_uid
        self.n_tokens_title = n_tokens_title
        self.n_tokens_raw_description = n_tokens_raw_description
