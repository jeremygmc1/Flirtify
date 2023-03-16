import psycopg
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

conn_string = "postgresql://jeremy:GvtUwDUhQOYrlDC7jEbblg@flirtify-4040.6xw.cockroachlabs.cloud:26257/flirtify.flirtify?sslmode=verify-full"

conn_params = {
    'host':"flirtify-4040.6xw.cockroachlabs.cloud",
    'port':"26257",
    'dbname':"flirtify",
    'user':"jeremy",
    'password':"GvtUwDUhQOYrlDC7jEbblg",
}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = conn_string
db = SQLAlchemy(app)
CORS(app)

# Configure the SQLAlchemy engine to use CockroachDB
engine = create_engine('cockroachdb://jeremy:GvtUwDUhQOYrlDC7jEbblg@flirtify-4040.6xw.cockroachlabs.cloud:26257/flirtify?sslmode=require')

# Create a SQLAlchemy session factory to manage database connections
Session = sessionmaker(bind=engine)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    preferences = db.Column(db.ARRAY(db.String))
    desiredFirstDate = db.Column(db.ARRAY(db.String))
    mbti = db.Column(db.String(4))
    email = db.Column(db.String(256))
    
    def __init__(self, firstname, lastname, gender, birthdate, age, preferences, desiredFirstDate, mbti, email):
        self.firstname = firstname
        self.lastname = lastname
        self.gender = gender
        self.birthdate = birthdate
        self.age = age
        self.preferences = preferences
        self.desiredFirstDate = desiredFirstDate
        self.mbti = mbti
        self.email = email

def get_conn():
    conn = psycopg.connect(**conn_params, autocommit=True)
    return conn

def run_sql(sql):
    with get_conn() as txn:
        txn.execute(sql)
        
def json(info):
    result = {"id":info[0], "firstname":info[1], "lastname":info[2], "gender":info[3], "birthdate":info[4], "age":info[5], "date_joined":info[6], "preferences":info[7], "desiredFirstDate":info[8], "mbti":info[9], "email":info[10]}
    return result
        

@app.route('/')
def index():
    
    return "Hello, World!"

session = Session()

@app.route("/user")
def get_all():
    user_search = get_conn().cursor().execute("SELECT * from public.users").fetchall()
    if len(user_search):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "users": [json(user) for user in user_search]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no users."
        }
    ), 404

@app.route("/user/<string:userid>")
def get_user(userid):
    user_search = get_conn().cursor().execute("SELECT * from public.users WHERE id = %s",(userid,)).fetchone()
    if (user_search):
        return jsonify(
            {
                "code": 200,
                "data": json(user_search)
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User not found."
        }
    ), 404
    
app.route("/user/create/<string:email>", methods=['POST'])
def create_user(email):
    user_search = get_conn().cursor().execute("SELECT * from public.users WHERE email = %s",(email,)).fetchone()
    if (user_search):
        return jsonify(
            {
                "code": 400,
                "data": json(user_search),
                "message": "User already exists."
            }
        ), 400
        
    data = request.get_json()
    user = User(**data)
    
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "email": email
                },
                "message": "An error occurred creating the user."
            }
        ), 500


if __name__ == '__main__':
    app.run(port=26257, debug=True)