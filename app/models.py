import datetime
from flask import current_app
from flask_login import UserMixin, current_user
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from sqlalchemy.orm import relationship
from . import db, login_manager


class RideRequest(db.Model):
    __tablename__ = 'riders'

    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    carpool_id = db.Column(db.Integer, db.ForeignKey('carpools.id'))
    person = db.relationship("Person")
    carpool = db.relationship("Carpool")
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow)
    status = db.Column(db.String(120))


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    description = db.Column(db.String(120))


class PersonRole(db.Model):
    __tablename__ = 'people_roles'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow)
    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


class Person(UserMixin, db.Model):
    __tablename__ = 'people'

    CONTACT_EMAIL = 'email'
    CONTACT_CALL = 'call'
    CONTACT_TEXT = 'text'
    CONTACT_METHODS = (
        CONTACT_EMAIL,
        CONTACT_CALL,
        CONTACT_TEXT,
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(14))
    name = db.Column(db.String(80))
    gender = db.Column(db.String(80))
    preferred_contact_method = db.Column(db.String(80))

    roles = db.relationship('Role', secondary='people_roles',
                            backref=db.backref('roles',
                                               lazy='dynamic'))

    def get_ride_requests_query(self, status=None):
        query = RideRequest.query.filter_by(person_id=self.id)

        if status:
            query = query.filter_by(status=status)

        return query

    def get_driving_carpools(self):
        query = Carpool.query.filter_by(driver_id=self.id)

        return query

    def has_roles(self, *roles):
        requested_role_set = set(roles)
        our_role_set = set(role.name for role in self.roles)

        return requested_role_set.issubset(our_role_set)


@login_manager.user_loader
def load_user(id):
    return Person.query.get(int(id))


class Carpool(db.Model):
    __tablename__ = 'carpools'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow)
    from_place = db.Column(db.String(120))
    from_point = db.Column(Geometry('POINT'))
    to_place = db.Column(db.String(120))
    to_point = db.Column(Geometry('POINT'))
    leave_time = db.Column(db.DateTime(timezone=True))
    return_time = db.Column(db.DateTime(timezone=True))
    max_riders = db.Column(db.Integer)
    driver_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))

    ride_requests = relationship("RideRequest", cascade="all, delete-orphan")

    def get_ride_requests_query(self, statuses=None):
        query = RideRequest.query.filter_by(carpool_id=self.id)

        if statuses:
            query = query.filter(RideRequest.status.in_(statuses))

        return query

    def get_current_user_ride_request(self):
        if current_user.is_anonymous:
            return False
        else:
            return self.get_ride_requests_query() \
                       .filter_by(person_id=current_user.id) \
                       .first()

    @property
    def current_user_is_driver(self):
        return current_user.id == self.driver_id

    @property
    def driver(self):
        return Person.query.get(self.driver_id)

    def get_riders(self, statuses):
        requests = self.get_ride_requests_query(statuses).all()

        if not requests:
            return []

        return Person.query.filter(
            Person.id.in_(p.person_id for p in requests)).all()

    @property
    def riders(self):
        return self.get_riders(['approved'])

    @property
    def riders_and_potential_riders(self):
        return self.get_riders(['approved', 'requested'])

    @property
    def seats_available(self):
        return self.max_riders - \
               self.get_ride_requests_query(['approved']).count()


class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow)
    hidden = db.Column(db.Boolean(), default=False)
    point = db.Column(Geometry('POINT'))
    name = db.Column(db.String(80))
    address = db.Column(db.String(300))

    @classmethod
    def find_all_visible(clz):
        return clz.query.filter(clz.hidden != True)

    def as_geojson(self):
        """ Returns a GeoJSON Feature object for this Destination. """
        return {
            "type": "Feature",
            "properties": {
                "name": self.name,
                "address": self.address,
            },
            "geometry": mapping(to_shape(self.point))
        }
