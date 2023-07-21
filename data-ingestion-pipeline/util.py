from datetime import datetime
import logging, pandas as pd, sys

# generic error object to serve as response type
class error(Exception):
    def __init__(self, status: bool = True,
        detail: str = "Oops, something might be wrong!", fatal: bool = True) -> None:
        self.status = status
        self.detail = detail
        self.fatal = fatal

# set up configuration for logging errors
def setup_logging() -> None:
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

# log errors cleanly in the terminal
def Log(err: error):
    logging.error(err.detail)
    if err.fatal:
        sys.exit(1)


# dataframe descriptor object for Node assimilation
class dfNode:
    def __init__(self, df: pd.DataFrame, label: str, primaryKey: str) -> None:
        self.df = df
        self.label  = label
        self.key = primaryKey

# convert date string to acceptable format for laoding into neo4j db
def convert_to_neo4j_date(date_string):
    # Parse the date string into a datetime object using the format "%m/%d/%y"
    date_object = datetime.strptime(date_string, "%d/%m/%y")

    # Format the datetime object into the Neo4j date format "YYYY-MM-DD"
    neo4j_date = date_object.strftime("%Y-%m-%d")
    
    return neo4j_date