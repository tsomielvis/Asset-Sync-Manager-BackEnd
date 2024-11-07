from app.config import db, bcrypt
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

class Asset(db.Model, SerializerMixin):
    __tablename__ = 'asset_table'

    serialize_rules = ('-assignments.asset', '-maintenances.asset', '-transactions.asset',)

    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    date_purchased = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_cost=db.Column(db.Float())
    image_url = db.Column(db.String(255))
    manufacturer = db.Column(db.String(255))
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50))
    category = db.Column(db.String(50))
    serial_number=db.Column(db.String())
    
    # Relationships
    assignments = db.relationship('Assignment', back_populates='asset')
    maintenances = db.relationship('Maintenance', back_populates='asset')
    transactions = db.relationship('Transaction', back_populates='asset')

    @validates('status')
    def validate_status(self, _, value):
        if value not in ['Active', 'Pending', 'Under Maintenance',"Sold"]:
            raise ValueError(f"Invalid status: {value}. Must be 'Active', 'Pending','Sold' or 'Under Maintenance'.")
        return value

class User(db.Model, SerializerMixin):
    __tablename__ = 'user'

    serialize_rules = ('-assignments.user', '-requests.user',"-_password_hash", "-email",)
  
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    _password_hash = db.Column('password_hash', db.String(255), nullable=False)
    role = db.Column(db.String(50))
    department = db.Column(db.String(255), nullable=False)
    employed_on = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assignments = db.relationship('Assignment', back_populates='user')
    requests = db.relationship('Requests', back_populates='user')

    @hybrid_property
    def password_hash(self):
        raise AttributeError('password hash may not be viewed')

    @password_hash.setter
    def password_hash(self, password):
        if password is not None:
            password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
            self._password_hash = password_hash.decode('utf-8')
        else:
            raise ValueError('Password cannot be None')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    @validates('email')
    def validate_email(self, key, value):
        if not value or '@' not in value:
            raise ValueError("Invalid email address.")
        return value

class Assignment(db.Model, SerializerMixin):
    __tablename__ = 'assignment'

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset_table.id'),nullable=False,unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignment_date = db.Column(db.Date)
    return_date = db.Column(db.Date)

    # Relationships
    asset = db.relationship('Asset', back_populates='assignments')
    user = db.relationship('User', back_populates='assignments')

    # Serialization rules
    serialize_rules = ('-asset.assignments', '-user.assignments',)

    @property
    def asset_name(self):
        return self.asset.asset_name if self.asset else None
    
    @property
    def name(self):
        return self.user.full_name if self.user else None
    
    



class Maintenance(db.Model, SerializerMixin):
    __tablename__ = 'maintenance'

    serialize_rules = ('-asset.maintenances',)
    
    maintenance_id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset_table.id'),nullable=False,unique=True)
    date_of_maintenance = db.Column(db.Date)
    type = db.Column(db.String(50))
    description = db.Column(db.String(255))
    cost = db.Column(db.Float)
    completion_status = db.Column(db.String(20))

    # Relationships
    asset = db.relationship('Asset', back_populates='maintenances')

class Transaction(db.Model, SerializerMixin):
    __tablename__ = 'transaction'

    serialize_rules = ('-asset.transactions',)

    transaction_id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('asset_table.id'),nullable=False,unique=True)
    transaction_type = db.Column(db.String(50))
    transaction_date = db.Column(db.Date)
    # Relationship
    asset = db.relationship('Asset', back_populates='transactions')

class Requests(db.Model, SerializerMixin):
    __tablename__ = 'requests'
    serialize_rules = ('-user.requests',"-user_id",)

    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    
    asset_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    quantity=db.Column(db.Integer())
    urgency=db.Column(db.String)
    status = db.Column(db.String(50))



    # Relationships
    user = db.relationship('User', back_populates='requests')

    @property
    def user_name(self):
        return self.user.full_name if self.user else None
