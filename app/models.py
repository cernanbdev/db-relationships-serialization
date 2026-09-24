from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True creates a UNIQUE constraint in the database itself.
    email = db.Column(db.String(255), nullable=False, unique=True)

    # One-to-one: uselist=False makes user.profile a single object, not a list.
    profile = db.relationship("Profile", back_populates="user", uselist=False)

    # One-to-many: user.documents is a list of Document objects.
    documents = db.relationship("Document", back_populates="owner")

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"


class Profile(db.Model):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(80), nullable=False)

    # unique=True is what makes this one-to-one IN THE DATABASE:
    # no two profiles can point at the same user.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    user = db.relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<Profile id={self.id} display_name={self.display_name!r}>"


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    source_url = db.Column(db.String(500), nullable=True)

    # The foreign key lives on the "many" side: many documents -> one user.
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document id={self.id} title={self.title!r}>"
