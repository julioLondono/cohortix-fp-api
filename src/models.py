from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    userFirstName = db.Column(db.String(45), nullable=False)
    userLastName = db.Column(db.String(45), nullable=False)
    userName = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(45), nullable=False)
    addresses = db.relationship('Address', backref='person', lazy=True)
    bill_address = db.relationship('BillingAddress', backref='person', lazy=True)

    def __repr__(self):
        return '<Person %r>' % self.userName

    def serialize(self):
        # need to create a dictionary (array) to be able to serialize by looping into an array
        addresses = []
        for i in self.addresses:
            # to display just the id uncomment the following line
            # addresses.append(i.id)
            #to display the entire object data
            addresses.append(i.serialize())
        billAddress = []
        for j in self.bill_address:
            billAddress.append(j.serialize())

        return {
            "user id": self.id,
            "userFirstName": self.userFirstName,
            "userLastName": self.userLastName,
            "userName": self.userName,
            "email": self.email,
            "password": self.password,
            "addresses": addresses,  #call the empty array that was looped before the return
            "Bill Address": billAddress
        }

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(45), unique=True, nullable=False)
    productDescription = db.Column(db.String(255), unique=True, nullable=True)
    productPrice = db.Column(db.String(45), unique=False, nullable=False)
    productCategory = db.Column(db.String(45), unique=False, nullable=True)
    productAgeRange = db.Column(db.String(45), unique=False, nullable=True)
    pictureUrl = db.relationship('Picture', backref='photos', lazy=True)
    # bill_address = db.relationship('BillingAddress', backref='person', lazy=True)

    def __repr__(self):
        return '<Product %r>' % self.productName

    def serialize(self):
        photo = []
        for i in self.pictureUrl:
            photo.append(i.serialize())
        return {
            "Product id": self.id,
            "ProductName": self.productName,
            "productDescription": self.productDescription,
            "productPrice": self.productPrice,
            "productCategory": self.productCategory,
            "productAgeRange": self.productAgeRange,
            "photo": photo
        }

class Address(db.Model):
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    userStreet = db.Column(db.String(45), nullable=False)
    userNumber = db.Column(db.String(45), nullable=False)
    userCity = db.Column(db.String(45), nullable=False)
    userState = db.Column(db.String(45), nullable=False)
    userZipCode = db.Column(db.String(12), nullable=False)
    isBillingAddress=db.Column(db.Boolean)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)


    def __repr__(self):
        return '<Addres %r>' % self.userStreet

    def serialize(self):
        return {
            "street id": self.id,
            "User Street": self.userStreet,
            "User Number": self.userNumber,
            "User City": self.userCity,
            "User State": self.userState,
            "User Zip Code": self.userZipCode,
            "Same as Billing Address": self.isBillingAddress,
            "user": self.person_id
        }

class BillingAddress(db.Model):
    __tablename__ = 'billing_addresses'

    id = db.Column(db.Integer, primary_key=True)
    billingStreet = db.Column(db.String(45), nullable=True)
    billingNumber = db.Column(db.String(45), nullable=True)
    billingCity = db.Column(db.String(45), nullable=True)
    billingState = db.Column(db.String(45), nullable=True)
    billingZipCode = db.Column(db.String(12), nullable=True)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)

    def __repr__(self):
        return '<BillingAddress %r>' % self.billingStreet

    def serialize(self):
        return {
            "Billing Street": self.billingStreet,
            "Billing Number": self.billingNumber,
            "Billing City": self.billingCity,
            "Billing State": self.billingState,
            "Billing Zip Code": self.billingZipCode,
            "user": self.person_id

        }

class Picture(db.Model):
    __tablename__ = 'pictures'

    id = db.Column(db.Integer, primary_key=True)
    picture_url = db.Column(db.Text, nullable=False)
    photos_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    # person_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    def __repr__(self):
        return '<Picture %r>' % self.picture_url

    def serialize(self):
        return {
            "Picture URL": self.picture_url,
            "product Id": self.photos_id
        }
