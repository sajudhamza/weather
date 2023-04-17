import pandas as pd
import os
import psycopg2
from sqlalchemy import create_engine
import logging
import time
from app import create

logger = logging.getLogger(__name__)



class PandasToPostgres:
    """
    Class to handle end to end lifecycle of data from a file directory
    """

    def __init__(self,
                 file_dir: str = "./wx_data/",
                 table_columns: list = ["date", "max_temp", "min_temp", "ppt", "station_id"],
                 user: str = "root",
                 password: str = "password",
                 host: str = "127.0.0.1",
                 database: str = "postgres",
                 table: str = "weather_record"):
        self.FILE_DIR = file_dir
        self.TABLE_COLUMNS = table_columns
        self.USER = user
        self.PASSWORD = password
        self.HOST = host
        self.DATABASE = database
        self.TABLE = table

    def create_station_dataset(self) -> pd.DataFrame:
        """

        :return: pandas dataframe created from the file directory
        """

        file_list = os.listdir(self.FILE_DIR)
        main_dataframe = pd.DataFrame(pd.read_csv(self.FILE_DIR + file_list[0], sep="\t", header=None))
        main_dataframe["station_id"] = file_list[0].replace(".txt", "")
        for i in range(1, len(file_list)):
            data = pd.read_csv(self.FILE_DIR + file_list[i], sep="\t", header=None)
            df = pd.DataFrame(data)
            df[1]= df[1]/10
            df[2]= df[2]/10
            df[3]= df[3]/10
            df["station_id"] = file_list[i].replace(".txt", "")
            main_dataframe = pd.concat([main_dataframe, df], axis=0)
        main_dataframe.columns = self.TABLE_COLUMNS
        return main_dataframe

    def insert_into_table(self, df: pd.DataFrame, table: str, if_exists: str = "append") -> None:
        """

        :param df: pandas dataset created from the file
        :param table: table in which data will be ingested
        :param if_exists: action to be performed if postgres table already exists
        :return: None
        """
        table = table or self.TABLE
        db = create_engine(f'postgresql+psycopg2://{self.USER}:{self.PASSWORD}@{self.HOST}/{self.DATABASE}',
                           pool_recycle=3600)
        conn = db.connect()
        try:
            print(f"Ingesting the data from files into the postgres table: {self.TABLE}")
            df.to_sql(name=table, con=conn, if_exists=if_exists, index=False)
        except ValueError as vx:
            logger.error(vx)
        except Exception as ex:
            logger.error(ex)
        else:
            print("PostgresSQL Table %s has been created successfully." % self.TABLE)
        finally:
            conn.close()

    def analysis(self, df: pd.DataFrame, date_col: str, station_col: str, analysis_col_with_operation: dict) \
            -> pd.DataFrame:
        """

        :param df: pandas dataset created from the file
        :param date_col: date column in the pandas dataset
        :param analysis_col_with_operation: column in which analysis is needed along with the operation to be performed on it
        :param station_col: station column i.e. common for all the analysis
        :return: final pandas dataframe
        """

        cols = [date_col, station_col]
        for analysis_col in analysis_col_with_operation.keys():
            df[analysis_col] = df[analysis_col].astype(float)
            # replacing missing values of -9999 in them with NULL
            df = df.replace({-9999: None})
            # creating dynamic columns to reduce levels of a df
            cols.append(f"{analysis_col}_{analysis_col_with_operation[analysis_col]}")
        df[date_col] = df[date_col].astype(str).str[:4]
        analysed_main_df = df.groupby([df[date_col], df[station_col]]).agg(analysis_col_with_operation)
        analysed_main_df = analysed_main_df.reset_index()
        analysed_main_df.columns = cols
        return analysed_main_df

    # testing
    def test_if_data_inserted(self) -> None:
        """

        :return: None
        """
        conn = psycopg2.connect(f'postgres://{self.USER}:{self.PASSWORD}@{self.HOST}/{self.DATABASE}')
        conn.autocommit = True
        cursor = conn.cursor()
        sql1 = f'''select * from {self.TABLE};'''
        cursor.execute(sql1)
        for i in cursor.fetchall():
            print(f"Fetching first value from newly created postgres table: {self.TABLE}")
            print(i)
            break


if __name__ == "__main__":
    create()
    ingest_data = PandasToPostgres()
    start_time = time.time()
    df = ingest_data.create_station_dataset()
    ingest_data.insert_into_table(df=df, table="weather_record")
    end_time = time.time()
    ingest_data.test_if_data_inserted()

    analysis_per_year = ingest_data.analysis(df=df,
                                             date_col="date",
                                             station_col="station_id",
                                             analysis_col_with_operation={"max_temp": "mean", "min_temp": "mean", "ppt": "sum"})
    print(f"Analysis per year per station having -> average max_temp, average min_temp, total ppt: {analysis_per_year}")
    ingest_data.insert_into_table(df=analysis_per_year, table="analysis_per_year")
    print(f"Start time: {start_time}", f"End time: {end_time}, Duration: {end_time - start_time} seconds.")






