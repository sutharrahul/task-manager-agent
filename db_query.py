from db import connect_db

# Add task
def add_task(title):
    cursor, connection, table_name = connect_db()
    cursor.execute(f"INSRT INTO {table_name} (title) VALUES (%s)", (title,))

    connection.commit()
    cursor.close()
    connection.close()

    return "Task add successfully"


# get all task
def get_all_taks(status=None):
    cursor, connection, table_name = connect_db()

    cursor.execute(f"SELECT * FROM {table_name}")

    all_taks = cursor.fetchall()

    cursor.close()
    connection.close()

    return all_taks


# get all task with status
def get_all_task_with_status(status=None):
    cursor, connection, table_name = connect_db()

    cursor.execute(f"SELECT * FROM {table_name} WHERE status = (%s)", (status,))

    all_taks = cursor.fetchall()

    cursor.close()
    connection.close()

    return all_taks


# check status of spefic task
def check_task_status(title):
    cursor, connection, table_name = connect_db()

    cursor.execute(f"SELECT status FROM {table_name} WHERE title = %s", (title,))
    get_task = cursor.fetchall()

    cursor.close()
    connection.close()

    return get_task


# update task
def update_task(title, status):
    cursor, connection, table_name = connect_db()

    cursor.execute(
        f"UPDATE {table_name} SET status = (%s) WHERE title = %s", (status, title)
    )
    
    update_task = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    return update_task, "Update task successfully"


# delete task
def delete_task(title, status):
    cursor, connection, table_name = connect_db()

    if title and status:
        cursor.execute(
            f"DELETE FROM {table_name} WHERE title = %s AND status = %s",
            (
                title,
                status,
            ),
        )
    elif title and not status:
        cursor.execute(f"DELETE FROM {table_name} WHERE title = %s", (title,))
    else:
        cursor.execute(f"DELETE FROM {table_name} WHERE status = %s", (status,))
    
    connection.commit()
    cursor.close()
    connection.close()

    return "Task deleted successfully"