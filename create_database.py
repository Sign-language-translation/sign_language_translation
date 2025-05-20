import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME')

# Database connection configuration
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
ignore_labels = [
    # 'bus',
    # 'name',
    # 'thanks',
    # 'now',
    # 'station'
    # # 'go',
    # 'help',
    # 'when',
    # 'phone',
    # 'come',
    # 'schedule',
    # 'hello',
    # 'doctor',
    # 'home',
    # 'need',
    # 'why',
    # 'arrive',
    # 'you',
    # 'clinic',
    # 'I',
    # 'place',
    # 'card',
    # 'idCard',
    # 'appointment',
    # 'later',
    # 'no',
    # 'ambulance',
]
# Define the VideoData table
class VideoData(Base):
    __tablename__ = 'video_data'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-increment primary key
    label = Column(String(255), nullable=False)  # Label for the word
    category = Column(String(100), nullable=True)  # Category of the word
    json_output = Column(Text, nullable=True)  # JSON output

# Create a database session
Session = sessionmaker(bind=engine)
session = Session()

# Function to extract label up to the first underscore
def extract_label(file_name):
    return file_name.split('_')[0]

# Function to add a single JSON file to the database
def add_json_file(file_path, category):
    try:
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        label = file_name.split("_")[0]
        if label not in ignore_labels:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_output = json.load(f)
            new_video = VideoData(
                label=label,
                category=category,
                json_output=json.dumps(json_output)  # Store JSON as a string
            )
            session.add(new_video)
            session.commit()
            print(f"Added JSON file '{file_path}' to the database with ID: {new_video.id}")
    except Exception as e:
        session.rollback()
        print(f"Failed to add JSON file '{file_path}': {e}")

def is_json_non_empty(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return bool(data)  # True if data is non-empty
    except Exception:
        return False

def add_json_files_from_folder(folder_path, category):
    defective_files = []


    try:
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.json'):
                file_path = os.path.join(folder_path, file_name)
                if is_json_non_empty(file_path):
                    add_json_file(file_path, category)
                else:
                    print(f"Skipped defective JSON file: {file_name}")
                    defective_files.append(file_name)
    except Exception as e:
        print(f"Failed to add JSON files from folder '{folder_path}': {e}")

    # Log defective files
    if defective_files:
        log_path = os.path.join(folder_path, 'defective_json_log.txt')
        with open(log_path, 'w', encoding='utf-8') as log_file:
            for file_name in defective_files:
                log_file.write(file_name + '\n')
        print(f"Logged {len(defective_files)} defective files to '{log_path}'")
# Function to read all records from the database and return a list of lists
def read_all():
    try:
        records = session.query(VideoData).all()
        result = [[record.id, record.label, record.category, record.json_output] for record in records]
        return result
    except Exception as e:
        print(f"Failed to read records: {e}")
        return []
    
def get_json_by_id(record_id):
    """
    Retrieve the JSON data from the database for the given ID and return it.
    
    Args:
        record_id (int): The ID of the record in the database.
        
    Returns:
         motion_data_old (dict): The JSON data as a Python dictionary.
    """
    try:
        # Query the database for the record with the given ID
        record = session.query(VideoData).filter_by(id=record_id).first()
        if not record:
            raise ValueError(f"No record found with ID {record_id}")

        # Load the JSON data from the record
        motion_data = json.loads(record.json_output)

        return motion_data
    
    except Exception as e:
        print(f"Failed to retrieve or convert data for ID {record_id}: {e}")
        return None

def create_db(folder_path = "resources/generated_motion_data"):
    Base.metadata.create_all(engine)
    print("Database and tables created successfully!")

    # Add all JSON files from a folder
    add_json_files_from_folder(folder_path, "first_model")

def drop_video_data_table():
    try:
        Base.metadata.drop_all(bind=engine, tables=[VideoData.__table__])
        print("Table 'video_data' dropped successfully.")
    except Exception as e:
        print(f"Failed to drop table 'video_data': {e}")

# Create the database tables
if __name__ == "__main__":
    create_db()