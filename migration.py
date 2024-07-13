from app import create_app, db
import os
import json
from datetime import datetime
from sqlalchemy import DateTime
from app.models import Streamer
from Twitch import Twitch
from config import Config
def create_JSON_db():
    app = create_app()
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
        existing_files = os.listdir('app/migration')
        db_files = [file for file in existing_files if file.startswith('db') and file.endswith('.json')]
        numbers = [int(file[2:-5]) for file in db_files if file[2:-5].isdigit()]
        next_number = max(numbers) + 1 if numbers else 1
        file_name = f"db{next_number}"
        with open(f"app/migration/{file_name}.json", 'w') as f:
            json.dump(data, f, default=str)
        print(f"Database saved to {file_name}.json")

def load_JSON_db(file_name, **function_migrations):
    app = create_app()
    with app.app_context():
        try:
            db.drop_all()
            db.create_all()
            with open(f"app/migration/{file_name}.json", 'r') as f:
                data = json.load(f)
                for table_name, rows in data.items():
                    table = db.metadata.tables[table_name]
                    column_names = [column.name for column in table.columns]
                    column_types = {column.name: column.type for column in table.columns}
                    for row in rows:
                        function_migration = function_migrations.get(table_name)
                        if function_migration:
                            row = function_migration(row)
                        data = {}
                        for column in column_names:
                            if isinstance(column_types[column], DateTime):
                                if isinstance(row[column], str) and row[column]:
                                    data[column] = datetime.strptime(row[column], "%Y-%m-%d %H:%M:%S")
                                else:
                                    data[column] = row[column]
                            else:
                                data[column] = row[column]
                        
                        insert = table.insert().values(**data)
                        db.session.execute(insert)
                db.session.commit()
                print(f"Database loaded from {file_name}.json")
                create_JSON_db()
        except Exception as e:
            db.session.rollback()
            print(e)

def import_streamer(file_path):
    app = create_app()
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

if __name__ == '__main__':
    # create_JSON_db()
    def test_migration(row):
        return row
    # load_JSON_db('db1', roles=test_migration)
    ...