from database.models import Base
from database.db import engine

Base.metadata.create_all(bind=engine)

# Python being a dynamically typed language, it will throw an error if there is any issue with the code or the database connection, which will prevent the print statement from executing. If the print statement executes, it means that the tables were created successfully without any exceptions.

print("Tables created!")
