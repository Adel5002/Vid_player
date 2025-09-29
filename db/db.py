from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "postgresql+psycopg2://anime:anime@db:5432/anime"

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session