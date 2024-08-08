'''
This module contains endpoints for debugging operations
related to the database.


@author: Emmanuel Olowu
@link: https://github.com/zeddyemy
@package: Trendit³
'''

from flask import Flask, request, current_app
from sqlalchemy import text
from ...extensions import db, limiter

from . import debugger
from ...utils.helpers.basic_helpers import log_exception
from ...utils.helpers.response_helpers import error_response, success_response
from ...models.user import Trendit3User



@debugger.route('/db', methods=['GET'])
@limiter.limit("5/hour")
def database_overview():
    """
    Provide an overview of the database structure.

    Returns:
        JSON response: A JSON response containing an overview of the database structure.
    """
    try:
        # Get a list of table names in the database
        table_names = [table.name for table in db.Model.metadata.tables.values()]

        total_tables = len(table_names) # Count the number of tables in the database

        # TODO: add more database-related information

        overview_data = {
            'total_tables': total_tables,
            'tables': table_names
        }
        return success_response('database overview fetched', 200, {'db_overview': overview_data})
    except Exception as e:
        log_exception('Exception', e)
        return error_response(f'Error: {str(e)}', 500)

@debugger.route('/db/tables')
@limiter.limit("2/hour")
def list_tables():
    """
    Retrieve a list of tables in the database.

    Returns:
        JSON response: A JSON response containing the list of tables.
    """
    try:
        table_names = []
        for table in db.Model.metadata.tables.values():
            table_names.append(table.name)
        return success_response('tables fetched', 200, {'tables': table_names})
    except Exception as e:
        log_exception('Exception', e)
        return error_response(f'Error: {str(e)}', 500)


@debugger.route('/db/table/<table_name>')
@limiter.limit("2/hour")
def table_info(table_name):
    """
    Retrieve information about a specific table in the database.

    Args:
        table_name (str): The name of the table.

    Returns:
        JSON response: A JSON response containing information about the specified table.
    """
    try:
        table = db.Model.metadata.tables.get(table_name)
        if table is None:
            return error_response(f'Error: {table_name} not found.', 404)
        
        columns = [{'name': column.name, 'type': str(column.type)} for column in table.columns]
        return success_response(f'columns for {table_name} fetched', 200, {'table': table_name, 'columns': columns})
    except Exception as e:
        log_exception('Exception', e)
        return error_response(f'Error: {str(e)}', 500)


@debugger.route('/db/delete', methods=['POST'])
@limiter.limit("2/hour")
def delete_record():
    """
    Delete a record from a specified table in the database.

    Returns:
        JSON response: A JSON response indicating the success or failure of the delete operation.
    """
    data = request.get_json()
    table_name = data.get('table')
    conditions = data.get('conditions')
    try:
        table = db.Model.metadata.tables[table_name]
        db.session.execute(table.delete().where(**conditions))
        db.session.commit()
        return success_response('Deleted', 200)
    except Exception as e:
        db.session.rollback()
        return error_response(f'Error: {str(e)}', 400)
