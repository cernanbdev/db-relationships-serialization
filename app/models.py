from app import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True creates a UNIQUE constraint in the database itself.
    email = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<User id={self.id} email={self.email!r}>"


# Coming up during the session:
#   01-one-to-many       Document (User has many Documents)
#   02-one-to-one        Profile (User has one Profile)
#   03-many-to-many      Tag + document_tags (Documents have many Tags, and vice versa)
#   04-document-chunks   Chunk (Document has many Chunks)
