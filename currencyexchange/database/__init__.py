from sqlalchemy import create_engine


def get_db_connection():
    return create_engine('sqlite:///college.db', echo = True)