from . import db
from sqlalchemy import func
from sqlalchemy.dialects.sqlite import JSON


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    image = db.Column(db.String(200))
    rating = db.Column(JSON)

    # Nuevos campos
    stock = db.Column(db.Integer, nullable=False, default=0)  # Cantidad en stock
    created_by = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # ID del admin que creó el producto
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    creator = db.relationship(
        "User", foreign_keys=[created_by], backref="products_created"
    )

    def __init__(
        self,
        title,
        price,
        description,
        category,
        image,
        rating=None,
        stock=0,
        created_by=None,
        created_at=None,
        updated_at=None,
    ):
        self.title = title
        self.price = price
        self.description = description
        self.category = category
        self.image = image
        if rating:
            self.rating_rate = rating.get("rate")
            self.rating_count = rating.get("count")
        self.stock = stock
        self.created_by = created_by
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at

        def __repr__(self):
            return f"<Product {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "image": self.image,
            "rating": {"rate": self.rating_rate, "count": self.rating_count},
            "stock": self.stock,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data.get("title"),
            price=data.get("price"),
            description=data.get("description"),
            category=data.get("category"),
            image=data.get("image"),
            rating=data.get("rating"),
            stock=data.get("stock"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
