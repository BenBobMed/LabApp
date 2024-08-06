import sqlite3
import os
import csv

def export_to_csv(db_path, export_folder):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
        return

    # Ensure the export folder exists
    os.makedirs(export_folder, exist_ok=True)

    # Iterate over all tables and export each to a CSV file
    for table_name in tables:
        table_name = table_name[0]  # Extract table name from tuple
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Fetch column names
        column_names = [description[0] for description in cursor.description]

        # Create CSV file for the table
        csv_file_path = os.path.join(export_folder, f"{table_name}.csv")
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(column_names)  # Write header
            writer.writerows(rows)  # Write data rows

        print(f"Table '{table_name}' exported to '{csv_file_path}'")

    # Close the database connection
    conn.close()

# Example usage:
db_path = 'userdata.db'  # Path to your SQLite database
export_folder = 'exported_tables'  # Folder where CSV files will be saved
export_to_csv(db_path, export_folder)
