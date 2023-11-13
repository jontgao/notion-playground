"""IMPORTANT NOTICE
This was written when I had read the instructions wrong (sad). Thus, this
assumes the page_id is for a database, and is written to add each element from
the CSV into a Notion database.
"""


"""Notion Take-Home Assessment.

Given a CSV file of book ratings of the form "book name, member name, rating",
generate a Notion database. Note that there are a variety of specifics detailed
in the assignment (e.g. what to do with duplicates, spacing, etc.)

See all details here:
https://www.notion.so/Intern-Take-Home-Exercise-ca75357f136d4557be6505632ed9bde0
"""
import os
from dotenv import load_dotenv
import pandas as pd
from enum import Enum
from notion_client import Client
import logging
from notion_client import APIErrorCode, APIResponseError

load_dotenv('.env')
notion = Client(auth=os.environ["NOTION_API_KEY"])
page_id = os.environ["NOTION_PAGE_ID"]

class Labels(str, Enum):
    BOOK = "Book Name"
    MEMBER = "Member Name"
    RATING = "Rating"

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

############################
# Notion database preprocessing
############################
def create_database():
    properties = {
        Labels.BOOK: {"id": Labels.BOOK, "title": {}},  # This is a required property
        Labels.MEMBER: {"id": Labels.MEMBER, "type": "rich_text", "rich_text": {}},
        Labels.RATING: {"id": Labels.RATING, "type": "number", "number": {"format": "number"}}
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

def update_database_properties(db):
    """Updates the id'd database's properties to match the assignment
    specifications.

    Args:
        db (dict): Original database's properties as a dictionary.

    Returns:
        Whether any changes were made to the properties.
    """
    changes_made = False

    if Labels.BOOK not in db["properties"].keys():
        rename_title_property(Labels.BOOK, db)
        changes_made = True
    if Labels.MEMBER not in db["properties"].keys():
        add_rich_text_property(Labels.MEMBER)
        changes_made = True
    if Labels.RATING not in db["properties"].keys():
        add_number_property(Labels.RATING)
        changes_made = True

    return changes_made

def rename_title_property(name, db):
    """Renames the title property to the given name.
    """
    for property_name, property_info in db["properties"].items():
        if property_info['id'] == 'title':
            try:
                notion.databases.update(database_id=page_id, 
                                    properties={property_name: {'name': name,}}
                                )
            except APIResponseError as error:
                logging.error(error)
                return            
            return

def add_rich_text_property(name):
    """Adds a rich text property.
    """
    try:
        notion.databases.update(database_id=page_id, 
                                properties={name: {
                                                'id': name,
                                                'name': name,
                                                'type': 'rich_text',
                                                'rich_text': {}
                                                }}
                               )
    except APIResponseError as error:
        logging.error(error)
        return
    
def add_number_property(name):
    """Adds a number property.
    """
    try:
        notion.databases.update(database_id=page_id, 
                            properties={name: {
                                               'id': name,
                                               'name': name,
                                               'type': 'number',
                                               'number': {'format': 'number'}
                                               }}
                               )
    except APIResponseError as error:
        logging.error(error)
        return

############################
# Importing data to Notion
############################
def import_df_to_notion(df):
    """Imports a pandas dataframe into a Notion database. Assumes properties
    will match.
    """
    for _, row in df.iterrows():
        potential_overlaps = get_book_rating_overlaps(row)["results"]
        
        if len(potential_overlaps) != 0: # assumes maximum one overlap
            update_book_rating(potential_overlaps[0]["id"], row)
        else:
            add_new_book_rating(row)                 

def retrieve_database():
    """Retrieves a database given its database_id.
    """
    try:
        return notion.databases.update(database_id=page_id)
    except APIResponseError as error:
        logging.error(error)
        return

def add_new_book_rating(row):
    """Adds a new book rating entry to database.
    """
    new_page = {
        Labels.BOOK: {"title": [{"text": {"content": row[Labels.BOOK]}}]},
        Labels.MEMBER: {
            "type": "rich_text",
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": row[Labels.MEMBER]},
                },
            ],
        },
        Labels.RATING: {
            "type": "number",
            "number": row[Labels.RATING],
        },
    }
    try:
        notion.pages.create(parent={"database_id": page_id}, properties=new_page)
    except APIResponseError as error:
        logging.error(error)
        return

def update_book_rating(entry_page_id, row):
    """Updates an existing book rating with a new rating. Book name and member
    name stay the same.
    """
    try:
        notion.pages.update(
            page_id=entry_page_id,
	        properties={
                Labels.RATING: {
                    "number": row[Labels.RATING]
                }
            }
        )
    except APIResponseError as error:
        logging.error(error)
        return
    
def archive_book_rating(entry_page_id):
    """Archives an existing book rating.
    """
    try:
        notion.pages.update(
            page_id=entry_page_id,
	        archived=True,
        )
    except APIResponseError as error:
        logging.error(error)
        return

def get_book_rating_overlaps(row):
    try:
        return notion.databases.query(database_id=page_id,
                                    filter={
                                        # "filter": {
                                            "and": [
                                                {
                                                    "property": Labels.BOOK,
                                                    "rich_text": {
                                                        "equals": row[Labels.BOOK]
                                                    }
                                                },
                                                {
                                                    "property": Labels.MEMBER,
                                                    "rich_text": {
                                                        "equals": row[Labels.MEMBER]
                                                    }
                                                }
                                            ]
                                        # }
                                    })
    except APIResponseError as error:
        logging.error(error)
        return

############################
# MAIN
############################
def main(file):
    df = prep_csv_to_df(file)
    create_database()
    # update_database_properties(retrieve_database())
    # import_df_to_notion(df)

main("assets/ratings.csv")