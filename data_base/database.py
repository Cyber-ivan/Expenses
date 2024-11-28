from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
from config import DB_SETTINGS

class DATABASE:

    def __init__(self):
        try:
            self.engine = create_engine(f"postgresql+psycopg2://{DB_SETTINGS['user']}:{DB_SETTINGS['password']}@{DB_SETTINGS['host']}/{DB_SETTINGS['dbname']}")
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(e)

    def execute_query(self, query, fetch_all=True):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                if fetch_all:
                    return result.fetchall()
                else:
                    return result.fetchone()
        except Exception as e:
            print(f"Ошибка: {e}")
            return f"Ошибка: {e}"

    def execute_transaction(self, query):
        try:
            with self.Session() as session:
                session.execute(text(query))
                session.commit()
                print("Транзакция выполнена успешно")
                return "Транзакция выполнена успешно!"
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return f"Ошибка выполнения запроса: {e}"

    def fetch_dataframe(self, query):
        try:
            with self.engine.connect() as connection:
                return pd.read_sql_query(query, connection)
        except Exception as e:
            print(f"Ошибка: {e}")
            return f"Ошибка: {e}"

