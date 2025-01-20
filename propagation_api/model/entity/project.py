from sqlalchemy import Column, BigInteger, String

from propagation_api.utils import Base


class Project(Base):
    __tablename__ = 'projects'

    id = Column(BigInteger, primary_key=True)  # Primary key column
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)

    def __repr__(self):
        return f"Project(id={self.id}, name='{self.name}', path={self.path})"

