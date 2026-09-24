from app import db


# Association table for the Document <-> Tag many-to-many relationship.
# It has no model class: each row just says "this document has this tag".
# The composite primary key stops the same tag being attached twice.
document_tags = db.Table(
    "document_tags",
    db.Column("document_id", db.Integer, db.ForeignKey("documents.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


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
    tags = db.relationship("Tag", secondary=document_tags, back_populates="documents", order_by="Tag.name")

    def __repr__(self):
        return f"<Document id={self.id} title={self.title!r}>"


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    documents = db.relationship("Document", secondary=document_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name!r}>"
