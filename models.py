from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class District(Base):
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    dropping_points = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    departures = relationship("Route", foreign_keys="Route.from_district_id", back_populates="origin")
    arrivals = relationship("Route", foreign_keys="Route.to_district_id", back_populates="destination")

class BusProvider(Base):
    __tablename__ = "bus_providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    coverage_districts = Column(JSON, nullable=False)
    official_address = Column(Text, nullable=True)
    contact_info = Column(String(200), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    privacy_policy = Column(Text, nullable=True)
    rating = Column(Float, default=4.0)
    total_buses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    routes = relationship("Route", back_populates="provider")
    bookings = relationship("Booking", back_populates="provider")

class Route(Base):
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("bus_providers.id"), nullable=False)
    from_district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    to_district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    base_fare = Column(Float, nullable=False)
    distance_km = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    seat_class = Column(String(20), default="Non-AC")
    available_seats = Column(Integer, default=40)
    total_seats = Column(Integer, default=40)
    departure_times = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    provider = relationship("BusProvider", back_populates="routes")
    origin = relationship("District", foreign_keys=[from_district_id], back_populates="departures")
    destination = relationship("District", foreign_keys=[to_district_id], back_populates="arrivals")
    bookings = relationship("Booking", back_populates="route")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(20), unique=True, index=True, nullable=False)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=True)
    provider_id = Column(Integer, ForeignKey("bus_providers.id"), nullable=True)
    
    # Passenger details
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100), nullable=True)
    
    # Journey details
    from_district = Column(String(100), nullable=False)
    to_district = Column(String(100), nullable=False)
    bus_provider = Column(String(100), nullable=False)
    dropping_point = Column(String(200), nullable=True)
    travel_date = Column(String(20), nullable=False)
    departure_time = Column(String(10), nullable=True)
    
    # Booking details
    seat_numbers = Column(JSON, nullable=True)
    num_seats = Column(Integer, default=1)
    fare = Column(Float, nullable=False)
    total_fare = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), default="active")
    payment_status = Column(String(20), default="pending")
    
    # Timestamps
    booking_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    route = relationship("Route", back_populates="bookings")
    provider = relationship("BusProvider", back_populates="bookings")
