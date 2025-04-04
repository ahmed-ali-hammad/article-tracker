from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Article(Base):
    """
    ORM model.
    """

    __tablename__ = "Article"

    pass
