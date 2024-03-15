import datetime

from sqlalchemy import Column, Integer, String, DateTime
from db import Base, engine, db_session


class Ads(Base):
    __tablename__ = "ads_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ads_id = Column(String(200), nullable=True, default=None)
    ads_url = Column(String(300), nullable=True, default=None)
    create_at = Column(DateTime, default=datetime.datetime.utcnow)

    @classmethod
    def create(cls, ads_id, ads_url) -> bool:
        with db_session() as session:
            row = session.query(cls).filter(cls.ads_id == ads_id).first()
            if row:
                return False
            record = cls(ads_id=ads_id, ads_url=ads_url)
            session.add(record)
            session.commit()
            return True


Base.metadata.create_all(engine)
