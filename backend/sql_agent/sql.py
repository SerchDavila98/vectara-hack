# Import required libraries and modules
import asyncio
import logging
from sqlalchemy import create_engine, text
from functools import partial
from langchain.agents import AgentType
from langchain import LLMChain, OpenAI, PromptTemplate, SQLDatabase
from langchain.agents import Tool, initialize_agent, tool
from langchain.chat_models import ChatOpenAI
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy import create_engine, MetaData
from langchain import PromptTemplate, OpenAI, LLMChain
import os
import json
from src.config import DATABASE_URL

def get_sql_db_schema(connection_string):
    """
    Retrieve the schema of the SQL database.

    Args:
        connection_string (str): The connection string for the database.

    Returns:
        dict: A dictionary representing the database schema.
    """
    try:
        # Create a SQLAlchemy engine using the provided connection string
        engine = create_engine(connection_string)

        # Create a MetaData object
        metadata = MetaData()

        # Reflect the database schema
        metadata.reflect(bind=engine)

        # Access the tables and columns using the MetaData object
        schema_dict = {}
        for table in metadata.sorted_tables:
            full_table_name = f"{table.schema}.{table.name}" if table.schema else table.name
            schema_dict[full_table_name] = [(column.name, str(column.type)) for column in table.columns]

        return schema_dict

    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_prompt_template(input_str: str, database_url: str) -> str:
    """
    Generate a prompt template based on input and database schema.

    Args:
        input_str (str): Input prompt.
        database_url (str): The URL for the database connection.

    Returns:
        str: Generated prompt template.
    """
    db_schema = get_sql_db_schema(database_url)
    if db_schema is None:
        return "Error: Unable to retrieve the database schema."
    schema_str = json.dumps(db_schema, indent=2)
    prompt_template = (
        f"Given this SQL database schema:\n\n{schema_str}\n\n"
        f"Return an SQL query to insert data into the database based on this prompt: {input_str}.\n"
        "You are only allowed to return the query in SQL language, nothing else, no text or anything else."
    )
    return prompt_template

@tool
def insert_data(input_str: str) -> str:
    """
    SQL insertion data tool.

    Args:
        input_str (str): User input.

    Returns:
        str: Result message.
    """
    # Safety check before generating SQL query
    safety_result = safetydelete_chain(input_str)
    if safety_result != "True":
        return "Error: Safety check failed. Your input indicates an attempt to delete data."

    # Prompt for generating SQL query based on input
    db_schema = get_sql_db_schema(DATABASE_URL)
    if db_schema is None:
        return "Error: Unable to retrieve the database schema."

    schema_str = json.dumps(db_schema, indent=2)
    template = generate_prompt_template(input_str, DATABASE_URL)

    prompt = PromptTemplate(template=template, input_variables=["schema", "input"])

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Generate SQL query using the prompt and user input
    query = llm_chain.predict(schema=schema_str, input=input_str)

    logging.info(query)

    try:
        # Create the SQLAlchemy engine
        engine = create_engine(DATABASE_URL)

        # Create a connection and execute the query
        with engine.connect() as connection:
            connection.execute(text(query))

        return "Data inserted successfully using SQLAlchemy"

    # Handle database errors using SQLAlchemyError:
    except SQLAlchemyError as error:
        logging.exception("SQLAlchemy error")
        return f"Error: {error}"

    # Handle other errors:
    except Exception as e:
        return f"Error: {e}"


def extract_data(input_str: str) -> str:
    """
    SQL extraction data tool.

    Args:
        input_str (str): User input.

    Returns:
        str: Extracted data.
    """
    # Safety check before generating SQL query
    safety_result = safetydelete_chain(input_str)
    if safety_result != "True":
        return "Error: Safety check failed. Your input indicates an attempt to delete data."

    # Prompt for generating SQL query based on input
    db_schema = get_sql_db_schema(DATABASE_URL)
    if db_schema is None:
        return "Error: Unable to retrieve the database schema."

    schema_str = json.dumps(db_schema, indent=2)
    template = generate_prompt_template(input_str, DATABASE_URL)

    prompt = PromptTemplate(template=template, input_variables=["schema", "input"])

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Generate SQL query using the prompt and user input
    query = llm_chain.predict(schema=schema_str, input=input_str)

    logging.info(query)

    try:
        # Create the SQLAlchemy engine
        engine = create_engine(DATABASE_URL)

        # Create a connection and execute the query
        with engine.connect() as connection:
            result = connection.execute(text(query))

            extracted_data = str(result.fetchall())

            return extracted_data

    # Handle database errors using SQLAlchemyError:
    except SQLAlchemyError as error:
        logging.exception("SQLAlchemy error")
        return f"Error: {error}"

    # Handle other errors:
    except Exception as e:
        return f"Error: {e}"

def AgentSQL(input):
    """
    Initialize and run AgentSQL.

    Args:
        input: User input.
    """
    SQL_query_tool = Tool(
            name="SQL query",
            func=extract_data,
            description="Useful when the input is a question",
        )

    SQL_in_tool = Tool(
            name="SQL input",
            func=insert_data,
            description="Useful when the input is a statement",
        )

    tools = [SQL_in_tool, SQL_query_tool]

    chat_model = ChatOpenAI(temperature=0,model_name="gpt-4")
    agent = initialize_agent(tools, chat_model, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    agent.run(input)

def process_input(input,discord_id,channel_id):
    """
    Run safety_chain and then AgentSQL based on safety check result.

    Args:
        input: User input.

    Returns:
        str: Safety result or None.
    """
    
    # Call the safetydelete_chain function first
    safety_result_delete = safetydelete_chain(input)

    # Check if the safety result is not True (failed)
    if safety_result_delete != "True":
        return safety_result_delete

    # Call the safetyinvalid_chain function
    safety_result_invalid = safetyinvalid_chain(input)

    # Check if the safety result is not True (failed)
    if safety_result_invalid != "True":
        return safety_result_invalid
    
    # Call the safetycomplete_chain function
    safety_result_complete = safetycomplete_chain(input)

    # Check if the safety result is not True (failed)
    if safety_result_complete != "True":
        return safety_result_complete

    # All safety checks passed, proceed with the AgentSQL function
    input = input + f"also the channel id is {channel_id} and the discord id is {discord_id} and it was created by {discord_id}."
    AgentSQL(input)

def safetycomplete_chain(input):
    """
    Perform safety chain checks.

    Args:
        input: User input.

    Returns:
        str: Safety result.
    """
    prompt_template = (
        "Make sure that the following message contains the answer to all of the following questions. "
        "If any of the questions are missing, please return 'I'm sorry but I believe you forgot to add...' "
        "and the missing information followed by 'Please invoke the Task Creation command again and add the missing info to your message "
        "(And re-insert the original input in quotes so they can copy-paste it, without the question mark)'. "
        "The questions are as follows:\n"
        "- What is the task name?\n"
        "- What is the task description?\n"
        "- When does the task start?\n"
        "- When is the due date?\n"
        "- When is the expected completion date?\n"
        "- Who is it assigned to or who is responsible for the task?\n"
        "If everything is there, return 'True'. The message is as follows: {input}."
    )

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )

    return llm_chain.run(input)

def safetydelete_chain(input):
    """
    Perform safety chain checks.

    Args:
        input: User input.

    Returns:
        str: Safety result.
    """
    prompt_template = (
        "Make sure that the following message does not contain anything with the intention of deleting a task or anything from a database. If it does please just return a nice message explaning that the message failed some safety checks about deletion of some data (do not explicitely say deltion of tasks or database) and possibly is intended to delete some information which is forbidden but be very nice about it add 'if you think there is an error feel free to contact the A1 team if there is anything else i can do for you let me know\n"
        "If everything is there, return 'True'.The message is as follows: {input}?"
    
    )

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )

    return llm_chain.run(input)

def safetyinvalid_chain(input):
    """
    Perform safety chain checks.

    Args:
        input: User input.

    Returns:
        str: Safety result.
    """
    prompt_template = (
        "Make sure that the following message does not contain describing a discord id or a channel or project id. please just return a nice message explaning that the message failed some safety checks about invalid inputs state that is probably related to users ids (do not explicitely say discord id or channel id) which could generate some issues in my (say my system not our) system but be very nice about it add 'if you think there is an error feel free to contact the A1 team if there is anything else i can do for you let me know do not say anything other than that\n"
        "If everything is there, return 'True'.The message is as follows: {input}?"
    
    )

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )

    return llm_chain.run(input)

