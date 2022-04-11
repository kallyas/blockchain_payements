import hashlib
# from pay_app import db


# class UserModel(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     wallet_address = db.Column(db.Text(), unique=True, nullable=False)
#     password = db.Column(db.String(80), nullable=False)

#     def __repr__(self):
#         return f'<User {self.username}>'

#     def save_to_db(self):
#         db.session.add(self)
#         db.session.commit()

#     @classmethod
#     def find_by_username(cls, username):
#         return cls.query.filter_by(username=username).first()

#     @classmethod
#     def update(cls):
#         db.session.commit()

#     @staticmethod
#     def generate_hash(password):
#         return hashlib.sha256(password.encode('utf-8')).hexdigest()

#     @classmethod
#     def verify_hash(cls, password, hash):
#         return hashlib.sha256(password.encode('utf-8')).hexdigest() == hash


class User:
    def __init__(self):
        self.users = []

    def add_user(self, username, password):
        return self.users.append({
            'id': len(self.users) + 1,
            'username': username,
            'password': self.hash_password(password)
        })


    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def authenticate(self, username, password):
        for user in self.users:
            if user['username'] == username and user['password'] == self.hash_password(password):
                return True
        return False

    def get_user_by_username(self, username):
        for user in self.users:
            if user['username'] == username:
                return user
        return None