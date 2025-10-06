from flask import Flask
from app import create_app, db
import os
import json
from datetime import datetime
from sqlalchemy import DateTime
from app.models import Streamer
from Twitch import Twitch
from config import Config
from typing import Callable
def create_JSON_db(app: Flask, create_file: bool = True):
    with app.app_context():
        db.create_all()
        tables = db.metadata.tables
        data = {}
        for table_name in tables:
            table = tables[table_name]
            column_names = [column.name for column in table.columns]
            rows = db.session.execute(table.select()).all()
            data[table.name] = [
                {column: value for column, value in zip(column_names, row)}
                for row in rows
            ]
        # créer le dossier migration
        if create_file:
            if not os.path.exists('app/migration'):
                os.makedirs('app/migration')
            existing_files = os.listdir('app/migration')
            db_files = [file for file in existing_files if file.startswith('db') and file.endswith('.json')]
            numbers = [int(file[2:-5]) for file in db_files if file[2:-5].isdigit()]
            next_number = max(numbers) + 1 if numbers else 1
            file_name = f"db{next_number}"
            with open(f"app/migration/{file_name}.json", 'w') as f:
                json.dump(data, f, default=str)
            print(f"Database saved to {file_name}.json")
            return file_name + ".json", data
        return None, data

def apply_migration(app: Flask, data:dict, table_name: str, change_table_name: Callable = None, **function_migrations):
    new_table_names = None
    if change_table_name:
        new_table_names = change_table_name(list(data.keys()))

    for table_name, rows in data.items():
        if new_table_names:
            table_name = new_table_names[table_name]
        if table_name == 'tokens':
            continue
        table = db.metadata.tables[table_name]
        column_names = [column.name for column in table.columns]
        column_types = {column.name: column.type for column in table.columns}
        for row in rows:
            function_migration = function_migrations.get(table_name)
            if function_migration:
                row = function_migration(row)
            data_row = {}
            for column in column_names:
                if isinstance(column_types[column], DateTime):
                    if isinstance(row[column], str) and row[column]:
                        data_row[column] = datetime.strptime(row[column], "%Y-%m-%d %H:%M:%S")
                    else:
                        data_row[column] = row[column]
                else:
                    data_row[column] = row[column]
            
            insert = table.insert().values(**data_row)
            db.session.execute(insert)
            db.session.commit()
        create_JSON_db(app, False)


def load_JSON_db(app: Flask, file_name, change_table_name: Callable = None, **function_migrations):
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            with open(f"app/migration/{file_name}", 'r') as f:
                data = json.load(f)
            apply_migration(app, data, file_name, change_table_name, **function_migrations)
        except Exception as e:
            db.session.rollback()
            print(f"An error occured while loading the database from {file_name}")
            print(e)
            db.session.rollback()

def load_latest_db(app: Flask):
    with app.app_context():
        existing_files = os.listdir('app/migration')
        db_files = [file for file in existing_files if file.startswith('db') and file.endswith('.json')]
        if not db_files:
            print("No database migration files found.")
            return
        numbers = [int(file[2:-5]) for file in db_files if file[2:-5].isdigit()]
        latest_number = max(numbers)
        latest_file = f"db{latest_number}.json"
        load_JSON_db(app, latest_file)
        print(f"Database loaded from {latest_file}")
                

def import_streamer(app: Flask, file_path: str):
    with app.app_context():
        Config.default()
        with open(file_path, 'r') as f:
            data = json.load(f)
            twitch = Twitch()
            for streamer in data:
                id_twitch, streamer_name = twitch.get_user_from_id(streamer['id_twitch'])
                Streamer.insert({
                    "id_twitch": id_twitch,
                    "pseudo": streamer_name
                })
def delete_guild_name(row:dict):
    if 'name' in row:
        row.pop('name')
    return row

def rename_discord_user_to_id_discord(row:dict):
    if 'discord_id' in row:
        row['id_discord'] = row.pop('discord_id')
    return row

if __name__ == '__main__':
    Config.default(migration=True)
    app = create_app()
    # load_latest_db(app)
    dbname, data = create_JSON_db(app)
    print(dbname)
    print(data)
    # def change_discordusers_to_discord_users(table_names:list)->dict:
    #     new_table_names = {}
    #     for table_name in table_names:
    #         if table_name == 'discordusers':
    #             new_table_names[table_name] = 'discord_users'
    #         else:
    #             new_table_names[table_name] = table_name
    #     return new_table_names
    # load_JSON_db('db8.json',change_table_name=change_discordusers_to_discord_users, discord_apps=delete_guild_name, discord_users=rename_discord_user_to_id_discord)
