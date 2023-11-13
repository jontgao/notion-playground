"""Notion Take-Home Assessment.

Given a CSV file of book ratings of the form "book name, member name, rating",
generate a new Notion database. Note that there are a variety of specifics
detailed in the assignment (e.g. what to do with duplicates, spacing, etc.)

See all details here:
https://www.notion.so/Intern-Take-Home-Exercise-ca75357f136d4557be6505632ed9bde0
"""

import logging
import numpy as np
import os
import pandas as pd

from enum import Enum
from dotenv import load_dotenv
from notion_client import APIResponseError, Client


load_dotenv('.env')
notion = Client(auth=os.environ["NOTION_API_KEY"])
page_id = os.environ["NOTION_PAGE_ID"]

class Labels(str, Enum):
    BOOK = "Book Name"
    MEMBER = "Member Name"
    RATING = "Rating"
    AVERAGE = "Average"
    FAVORITES = "Favorites"

############################
# CSV preprocessing
############################
def prep_csv_to_df(file):
    """Converts a CSV file of book ratings to a pandas dataframe. If there are
    repeat ratings (same BOOK and MEMBER), keeps the last.
    """
    # NOTE: since capitalization and whitespace at front/back are not
    # considered, we standardize them (titlecase, strip whitespace)
    # NOTE: does not check if ratings are actually in range [0, 5]
    df = pd.read_csv(file, names=[e.value for e in Labels])
    df[Labels.BOOK] = df[Labels.BOOK].str.title().str.strip()
    df[Labels.MEMBER] = df[Labels.MEMBER].str.title().str.strip()
    df = df.drop_duplicates(
        subset=[Labels.BOOK, Labels.MEMBER],
        keep="last"
    )
    
    return df

def analyze_df(df):
    """Returns the average rating and number of favorites for each book as a
    dataframe.
    """
    return df.groupby([Labels.BOOK], as_index=False).agg(
        Average=(Labels.RATING, np.mean),
        Favorites=(Labels.RATING, lambda x: np.count_nonzero(x == 5))
    )

############################
# Notion database preprocessing
############################
def create_database():
    """Creates a new database with the needed properties for the
    assignment (average, favorites).
    """
    properties = {
        Labels.BOOK: {"id": Labels.BOOK, "title": {}},  # This is a required property
        Labels.AVERAGE: {"id": Labels.AVERAGE, "type": "number", "number": {"format": "number"}},
        Labels.FAVORITES: {"id": Labels.FAVORITES, "type": "number", "number": {"format": "number"}}
    }
    title = [{"type": "text", "text": {"content": "Book Ratings"}}]
    parent = {"type": "page_id", "page_id": page_id}

    try:
        return notion.databases.create(
            parent=parent,
            title=title,
            properties=properties
        )
    except APIResponseError as error:
        logging.error(error)
        return  

############################
# Importing data to Notion
############################
def import_df_to_notion(df, database_id):
    """Imports a pandas dataframe into a Notion database. Assumes properties
    will match.
    """
    for _, row in df.iterrows():
        add_new_book_rating(row, database_id)                 

def add_new_book_rating(row, database_id):
    """Adds a new book rating entry to database.
    """
    new_page = {
        Labels.BOOK: {"title": [{"text": {"content": row[Labels.BOOK]}}]},
        Labels.AVERAGE: {
            "type": "number",
            "number": row[Labels.AVERAGE],
        },
        Labels.FAVORITES: {
            "type": "number",
            "number": row[Labels.FAVORITES],
        },
    }
    try:
        notion.pages.create(parent={"database_id": database_id["id"]}, properties=new_page)
    except APIResponseError as error:
        logging.error(error)
        return

############################
# MAIN
############################
def main(file):
    df = prep_csv_to_df(file)
    df = analyze_df(df)
    database_id = create_database()
    import_df_to_notion(df, database_id)

main("assets/ratings.csv")