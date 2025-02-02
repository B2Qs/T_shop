from . import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    image = db.Column(db.String(200))
    rating_rate = db.Column(db.Float)
    rating_count = db.Column(db.Integer)

    def __init__(self, title, price, description, category, image, rating=None):
        self.title = title
        self.price = price
        self.description = description
        self.category = category
        self.image = image
        if rating:
            self.rating_rate = rating.get('rate')
            self.rating_count = rating.get('count')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'description': self.description,
            'category': self.category,
            'image': self.image,
            'rating': {
                'rate': self.rating_rate,
                'count': self.rating_count
            }
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            price=data.get('price'),
            description=data.get('description'),
            category=data.get('category'),
            image=data.get('image'),
            rating=data.get('rating')
        )
