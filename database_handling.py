# =====================================================
# Copyright © 2026 Russell Rags. All Rights Reserved.
# Project: System Status Discord Bot
# =====================================================


import sqlite3


# The name/location of our database file.
#
# Since system.db is in the same folder as this file,
# we can just use the filename.
DATABASE = "alterDB.db"



# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_connection():
    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection

def create_messages_table():
    db = get_database_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Messages (
            message_id INTEGER PRIMARY KEY,
            message TEXT,
            alter_id INTEGER,
            disc_id_recpt INTEGER,
            alter_or_user INTEGER,
            date_created TEXT
        )
        """
    )

    db.commit()
    db.close()

create_messages_table()

# ============================================================
# CURRENT FRONTER FUNCTIONS
# ============================================================


def get_current_fronter():
    """
    Gets the current fronter from the database.

    Returns:
        The name of the current fronter as text.
    """

    # Open database connection
    db = get_database_connection()

    # Cursor is what actually runs SQL commands
    cursor = db.cursor()


    # Ask SQLite for the CurrentFronter value.
    #
    # We use ID = 1 because SystemStatus should
    # only have one row.
    cursor.execute(
        """
        SELECT CurrentFronter
        FROM SystemStatus
        WHERE ID = 1
        """
    )


    # fetchone() gets the first result.
    #
    # SQL returns something like:
    #
    # ("Mars",)
    #
    # The comma exists because it is a tuple.
    result = cursor.fetchone()


    # Close database connection
    db.close()



    # If a result exists, return the actual name.
    #
    # result[0] turns:
    #
    # ("Mars",)
    #
    # into:
    #
    # Mars
    if result:
        return result[0]


    # If there is somehow no fronter,
    # return a default value.
    return "Unknown"



def set_current_fronter(new_fronter):
    """
    Updates the current fronter in the database.

    Parameters:
        new_fronter (str):
            The new fronter name.
    """


    # Open database connection
    db = get_database_connection()

    # Create SQL cursor
    cursor = db.cursor()



    # Update the current fronter.
    #
    # The ? is a placeholder.
    #
    # NEVER do:
    #
    # "UPDATE SystemStatus SET CurrentFronter = '" + new_fronter + "'"
    #
    # because that can cause SQL injection problems.
    cursor.execute(
        """
        UPDATE SystemStatus
        SET CurrentFronter = ?
        WHERE ID = 1
        """,
        (new_fronter,)
    )



    # Save the change.
    #
    # Without commit(), the change disappears
    # when the connection closes.
    db.commit()



    # Close connection
    db.close()



# ============================================================
# ALTER FUNCTIONS
# ============================================================


def get_alters():
    """
    Gets every alter from the database.

    Returns:
        A list containing all alter records.
    """

    db = get_database_connection()

    cursor = db.cursor()



    # Select all alters.
    #
    # We get:
    # ID
    # Name
    # Pronouns
    # Role
    #
    cursor.execute(
        """
        SELECT ID, Name, Pronouns, Role
        FROM Alters
        """
    )


    # fetchall() returns every result.
    #
    # Example:
    #
    # [
    #   (1, "Mars", "She/Her", "Protector"),
    #   (2, "Casper", "He/Him", "Chaos")
    # ]
    alters = cursor.fetchall()


    db.close()


    return alters

def get_alter_name(alter_id):
    conn = sqlite3.connect("AlterDB.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT Name FROM Alters WHERE ID = ?",
        (alter_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def get_alter_id_by_name(alter_name):
    conn = sqlite3.connect("AlterDB.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT ID FROM Alters WHERE Name = ?",
        (alter_name,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def add_alter(name, pronouns, role, image_url=None):
    """
    Adds a new alter to the database.

    Parameters:
        name:
            Alter name

        pronouns:
            Alter pronouns

        role:
            Optional role description
    """

    db = get_database_connection()

    cursor = db.cursor()



    cursor.execute(
        """
        INSERT INTO Alters
        (Name, Pronouns, Role, image_url)
        VALUES (?, ?, ?, ?)
        """,
        (
            name,
            pronouns,
            role,
            image_url
        )
    )


    # Save changes
    db.commit()


    db.close()

def remove_alter(alter_id):
    """
    Removes an alter from the database.

    Parameters:
        alter_id:
            The database ID of the alter.
    """

    db = get_database_connection()

    cursor = db.cursor()


    cursor.execute(
        """
        DELETE FROM Alters
        WHERE ID = ?
        """,
        (alter_id,)
    )


    db.commit()

    db.close()
    
def get_alter_names():
    db = get_database_connection()

    try:
        cursor = db.cursor()

        cursor.execute(
            "SELECT Name FROM Alters"
        )

        return [row[0] for row in cursor.fetchall()]

    finally:
        db.close()

def update_alter(alter_id, name=None, pronouns=None, role=None, image_url=None):
    """
    Updates an existing alter's information.

    Only fields that are provided get changed —
    anything left as None stays the same in the database.

    Parameters:
        alter_id:
            The database ID of the alter to update.

        name (optional):
            New name for the alter.

        pronouns (optional):
            New pronouns for the alter.

        role (optional):
            New role for the alter.

    Returns:
        True if the update happened.
        False if no fields were given to update.
    """

    if name is None and pronouns is None and role is None and image_url is None:
        return False

    db = get_database_connection()

    cursor = db.cursor()

    fields = []
    values = []

    if name is not None:
        fields.append("Name = ?")
        values.append(name)

    if pronouns is not None:
        fields.append("Pronouns = ?")
        values.append(pronouns)

    if role is not None:
        fields.append("Role = ?")
        values.append(role)

    if image_url is not None:
        fields.append("Image_URL = ?") 
        values.append(image_url)
        
    values.append(alter_id)

    query = f"""
        UPDATE Alters
        SET {", ".join(fields)}
        WHERE ID = ?
    """

    cursor.execute(query, values)

    db.commit()

    db.close()

    return True

def get_alter_by_id(alter_id):
    

    db = get_database_connection()

    cursor = db.cursor()

    cursor.execute(
        """
        SELECT ID, Name, Pronouns, Role, Image_URL
        FROM Alters
        WHERE ID = ?
        """,
        (alter_id,)
    )

    result = cursor.fetchone()

    db.close()

    return result

def create_new_message(Message, Alter_ID, Recpt_ID, alter_or_user, current_time, sender_disc_id):
    db = get_database_connection()
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO Messages (message, alter_id, disc_id_recpt, alter_or_user, date_created, sender_disc_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (Message, Alter_ID, Recpt_ID, alter_or_user, current_time, sender_disc_id)
        )
        db.commit()
    finally:
        db.close()
    
def read_message_user(ID):
        
    db = get_database_connection()
    
    cursor = db.cursor()
     
    cursor.execute(
            """
            SELECT alter_id, message, message_id, date_created
            FROM Messages
            WHERE disc_id_recpt = ?
            """,
            (ID,)
        )
    
    result = cursor.fetchall()
    
    db.close()   
    
    return result         

def read_host_id():
    db = get_database_connection()
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT host_id
            FROM CoreInfo
            """
        )
        result = cursor.fetchone()
        return result
    finally:
        db.close()

def set_host_id(host_id):
    db = get_database_connection()
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO CoreInfo (host_id)
            VALUES (?)
            """,
            (host_id,)
        )
        db.commit()
    finally:
        db.close()
        
def read_message_alter(alter_id): 
    db = get_database_connection()
     
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT message_id, message, date_created
        FROM Messages
        WHERE alter_id = ?
        """,
        (alter_id,)
        ) 
       
    result = cursor.fetchall()
       
    db.close 
    
    return result 

        
        
def ban_user(user_ID, reason ):
    db = get_database_connection()
    try:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO banned_users (BannedID, Reason)
            VALUES (?, ?)
            """,
            (user_ID, reason)
        )
        db.commit()
    finally:
        db.close()