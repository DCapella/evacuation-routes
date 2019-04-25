import os

project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, 'addressdatabase.db')
database_file = f'sqlite:///{db_path}'

