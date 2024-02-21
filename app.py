import os
from flask import Flask
from flask_cors import CORS
from sqlalchemy import inspect
from routes.authorization import auth_bp
from routes.projects import project_bp
from routes.trackers import tracker_bp
from routes.items import item_bp
from routes.associations import association_bp
from routes.users import user_bp
from models import db, Project, Tracker, Item, User, Status, Association, CodebeamerEntityReference, Field

app = Flask(__name__)
app.url_map.strict_slashes = False

# if Database_URL is set replace "postgres://" with "postgresql://" and if not set use sqlite
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db.init_app(app)


app.register_blueprint(auth_bp, url_prefix='/auth',)
app.register_blueprint(project_bp, url_prefix='/cb/api/v3/projects')
app.register_blueprint(tracker_bp, url_prefix='/cb/api/v3/trackers')
app.register_blueprint(item_bp, url_prefix='/cb/api/v3/items')
app.register_blueprint(association_bp, url_prefix='/cb/api/v3/associations')
app.register_blueprint(user_bp, url_prefix='/cb/api/v3/users')

# @app.after_request
# def after_request(response):
#   response.headers.add('Access-Control-Allow-Origin', '*')
#   response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#   response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#   response.headers.add('Access-Control-Allow-Credentials', 'true')
#   return response

# create a route that removes all db data and repulates
@app.route('/reset')
def reset():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        inspector = inspect(db.engine)
        if table.name in inspector.get_table_names():
            db.session.execute(table.delete())

    db.session.commit()
    repopulate()

    return "Database reset and repopulated"

def repopulate():
    with app.app_context():
        # Create the database tables
        db.create_all()

        # Sample data for initialization
        sample_project = Project(name="Test Project")
        db.session.add(sample_project)

        sample_tracker = Tracker(name="Test Tracker", keyName="testKey", color="red", project_id=1)
        db.session.add(sample_tracker)

        sample_user_1 = User(name="baumgae5", email="ethan.baumgartner@roche.com")
        user_value = CodebeamerEntityReference(name="baumgae5", type="UserReference")
        db.session.add(sample_user_1)
        db.session.add(user_value)
        sample_user_2 = User(name="test1", email="test1@test.test")
        db.session.add(sample_user_2)
        sample_user_3 = User(name="test2", email="test2@test.test")
        db.session.add(sample_user_3)

        sample_status = Status(name="Test Status", type="Test Type")
        db.session.add(sample_status)

        sample_team_value = CodebeamerEntityReference(id=542154, name="Rainbow", type="TrackerItemReference")

        sample_item_1 =  Item(name="Test Item 1", description="Test Description", descriptionFormat="Wiki", storyPoints=5, tracker_id=1, status=[sample_status], assignedTo=[sample_user_1], teams=[sample_team_value])
        db.session.add(sample_item_1)
        sample_item_2 =  Item(name="Test Item 2", description="Test Description", descriptionFormat="Wiki", storyPoints=5, tracker_id=1, status=[sample_status], assignedTo=[sample_user_1], teams=[sample_team_value])
        db.session.add(sample_item_2)

        sample_name_field_1 = Field(name="name", type="Test Type", trackerId=1, itemId=1)
        sample_name_field_2 = Field(name="name", type="Test Type", trackerId=1, itemId=2)
        db.session.add(sample_name_field_1)
        db.session.add(sample_name_field_2)
        sample_description_field_1 = Field(name="description", type="Test Type", trackerId=1, itemId=1)
        sample_description_field_2 = Field(name="description", type="Test Type", trackerId=1, itemId=2)
        db.session.add(sample_description_field_1)
        db.session.add(sample_description_field_2)
        sample_story_points_field_1 = Field(name="storyPoints", type="Test Type", trackerId=1, itemId=1)
        sample_story_points_field_2 = Field(name="storyPoints", type="Test Type", trackerId=1, itemId=2)
        db.session.add(sample_story_points_field_1)
        db.session.add(sample_story_points_field_2)

        sample_assigned_to_field_1 = Field(name="assignedTo", type="ChoiceFieldValue", trackerId=1, itemId=1, values=[user_value])
        sample_assigned_to_field_2 = Field(name="assignedTo", type="ChoiceFieldValue", trackerId=1, itemId=2, values=[user_value])
        db.session.add(sample_assigned_to_field_1)
        db.session.add(sample_assigned_to_field_2)

        db.session.add(sample_team_value)
        sample_team_field_1 = Field(name="teams", type="ChoiceFieldValue", trackerId=1, itemId=1, values=[sample_team_value])
        sample_team_field_2 = Field(name="teams", type="ChoiceFieldValue", trackerId=1, itemId=2, values=[sample_team_value])
        db.session.add(sample_team_field_1)
        db.session.add(sample_team_field_2)


        sample_association_from = CodebeamerEntityReference(name="Test Item 1")
        db.session.add(sample_association_from)
        sample_association_to = CodebeamerEntityReference(name="Test Item 2")
        db.session.add(sample_association_to)
        sample_association_type = CodebeamerEntityReference(name="OutgoingTrackerItemAssociation")
        db.session.add(sample_association_type) 

        db.session.commit()

        sample_association = Association(description="Test Description", from_id=1, to_id=2, type_id=3)
        db.session.add(sample_association)
        
        db.session.commit()

@app.route('/')
def welcome():
    return """
    <h1>Welcome to the OAuth2 Token Retrieval Service!</h1>
    <p>This Flask app serves as a simple OAuth2 token retrieval service.</p>
    <p>Use the '/token' endpoint with a POST request to obtain a access token containing the id token value from googles token endpoint.</p>
    """



if __name__ == "__main__":
    CORS(app, supports_credentials=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
