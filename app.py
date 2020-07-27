from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt
import io

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://tqmfpzqbmtjvcm:742ecd784774054bec2b8339a965bb1431d368efaa835c9dd07da324d660659a@ec2-54-159-138-67.compute-1.amazonaws.com:5432/dci8igh6qvi1ht"



db = SQLAlchemy(app)
ma = Marshmallow(app)

heroku = Heroku(app)
CORS(app)
bcrypt = Bcrypt(app)


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(), nullable=False)
    password_confirm = db.Column(db.String(), nullable=False)
    address1 = db.Column(db.String(), nullable=False)
    address2 = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(15), nullable=False)
    state = db.Column(db.String(4), nullable=False)
    zipcode = db.Column(db.Integer(), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    

    def __init__(self, first_name, last_name, email, username, password, address1, address2, city, state, zipcode, data, user_id):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = password
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zipcode= zipcode
        self.data = data
        self.user_id = user_id

class ProfileSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "username", "password", "address1", "address2", "city", "state", "zipcode", "data", "user_id")    

profile_schema = ProfileSchema()
profiles_schema = ProfileSchema(many=True)




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    user_profiles = db.relationship("Profile", cascade="all,delete", backref="user", lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@app.route("/profile/add", methods=["POST"])
def add_profile():
    name = request.form.get("name")
    file_type = request.form.get("type")
    data = request.files.get("data")
    username = request.form.get("username")

    user_id = db.session.query(User.id).filter(User.username == username).first()

    new_profile = Profile(name, file_type, data.read(), user_id[0])
    db.session.add(new_file)
    db.session.commit()

    return jsonify("File Added Succesfully")

@app.route("/image/add", methods=["POST"])  
def add_image():
    file = request.files['image']  
    img = Image.open(file.stream)

    return jsonify({'msg': 'success', 'size' : [img.width, img.height]})

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(users_schema.dump(all_users))    


@app.route("/user/create", methods=["POST"])
def create_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("usernameInput")
    password = post_data.get("passwordInput")
    password_confirm = post_data.get("passwordConfirmInput")
    first_name = post_data.get("firstName")
    last_name = post_data.get("lastName")
    email = post_data.get("email")
    address1 = post_data.get("address1")
    address2 = post_data.get("address2")
    city = post_data.get("city")
    state = post_data.get("state")
    zipcode = post_data.get("zipCode")
    

    username_check = db.session.query(User.username).filter(User.username == username).first()
    if username_check is not None:
        return jsonify("Username Taken")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf8")

    record = Profile(username, hashed_password, first_name, last_name, email, address1, address2, city, state, zipcode)
    db.session.add(record)
    db.session.commit()

    return jsonify("User Created Successfully")    



@app.route("/user/verification", methods=["POST"])
def verify_user():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON")

    post_data = request.get_json()
    username = post_data.get("usernameInput")
    password = post_data.get("passwordInput")

    stored_password = db.session.query(User.password).filter(User.username == username).first()

    if stored_password is None:
        return jsonify("User NOT Verified")

    valid_password_check = bcrypt.check_password_hash(stored_password[0], password)

    if valid_password_check == False:
        return jsonify("User NOT Verified")

    return jsonify("User Verified")    












if __name__ == "__main__":
    app.run(debug=True)