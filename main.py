from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import os
import random
import string

from database import engine, get_db, Base
from models import District, BusProvider, Booking, Route
from rag_pipeline import rag_pipeline

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bus Ticket Booking System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models
class BookingRequest(BaseModel):
    customer_name: str
    customer_phone: str
    from_district: str
    to_district: str
    bus_provider: str
    dropping_point: Optional[str] = ""
    travel_date: str

class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    customer_name: str
    customer_phone: str
    from_district: str
    to_district: str
    bus_provider: str
    dropping_point: str
    fare: float
    travel_date: str
    booking_date: datetime
    status: str

class SearchQuery(BaseModel):
    query: str

def generate_booking_reference():
    """Generate unique booking reference"""
    return 'BK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

@app.on_event("startup")
async def startup_event():
    """Initialize database with data from data.json"""
    db = next(get_db())
    
    # Check if data already exists
    if db.query(District).count() == 0:
        with open('data.json', 'r') as f:
            data = json.load(f)
        
        # Load districts
        district_map = {}
        for district_data in data['districts']:
            district = District(
                name=district_data['name'],
                dropping_points=district_data['dropping_points'],
                description=f"Travel destination in Bangladesh",
                is_active=True
            )
            db.add(district)
            db.flush()
            district_map[district.name] = district
        
        # Load bus providers with their privacy policy info
        provider_map = {}
        for provider_data in data['bus_providers']:
            provider_info = rag_pipeline.get_provider_info(provider_data['name'])
            privacy_text = ""
            official_address = ""
            contact = ""
            email = ""
            website = ""
            
            if provider_info:
                privacy_text = provider_info['content']
                # Extract contact info from content
                lines = provider_info['content'].split('\n')
                for line in lines:
                    if 'Official Address:' in line:
                        official_address = line.split(':', 1)[-1].strip()
                    elif 'Contact Information:' in line or 'Tel:' in line or 'Call Center' in line:
                        contact = line.split(':', 1)[-1].strip()
                    elif 'email' in line.lower() and '@' in line:
                        parts = line.split()
                        for part in parts:
                            if '@' in part:
                                email = part.strip()
                    elif 'Privacy Policy / Terms Link:' in line or 'http' in line:
                        parts = line.split()
                        for part in parts:
                            if 'http' in part:
                                website = part.strip()
            
            provider = BusProvider(
                name=provider_data['name'],
                coverage_districts=provider_data['coverage_districts'],
                official_address=official_address,
                contact_info=contact,
                email=email,
                website=website,
                privacy_policy=privacy_text,
                rating=4.0 + (hash(provider_data['name']) % 10) / 10,  # Generate ratings 4.0-4.9
                total_buses=10 + (hash(provider_data['name']) % 20),  # 10-30 buses
                is_active=True
            )
            db.add(provider)
            db.flush()
            provider_map[provider.name] = provider
        
        # Create routes between districts for each provider
        base_fares = {
            ('Dhaka', 'Chattogram'): 600, ('Dhaka', 'Sylhet'): 700, ('Dhaka', 'Rajshahi'): 480,
            ('Dhaka', 'Khulna'): 500, ('Dhaka', 'Barishal'): 450, ('Dhaka', 'Rangpur'): 550,
            ('Dhaka', 'Mymensingh'): 300, ('Dhaka', 'Comilla'): 350, ('Dhaka', 'Bogra'): 420,
            ('Chattogram', 'Sylhet'): 400, ('Chattogram', 'Cox\'s Bazar'): 350,
            ('Khulna', 'Rajshahi'): 300, ('Khulna', 'Jessore'): 150,
        }
        
        for provider in provider_map.values():
            covered = provider.coverage_districts
            for i, from_district in enumerate(covered):
                for to_district in covered[i+1:]:
                    # Get or estimate fare
                    fare_key = (from_district, to_district)
                    reverse_key = (to_district, from_district)
                    base_fare = base_fares.get(fare_key, base_fares.get(reverse_key, 400))
                    
                    # Add some variation per provider
                    fare = base_fare + (hash(provider.name + from_district) % 100)
                    
                    if from_district in district_map and to_district in district_map:
                        # Create route in both directions
                        route1 = Route(
                            provider_id=provider.id,
                            from_district_id=district_map[from_district].id,
                            to_district_id=district_map[to_district].id,
                            base_fare=fare,
                            distance_km=200 + (hash(from_district + to_district) % 300),
                            duration_hours=3 + (hash(from_district + to_district) % 6),
                            seat_class="AC" if hash(provider.name) % 2 == 0 else "Non-AC",
                            available_seats=35 + (hash(from_district) % 10),
                            total_seats=40,
                            departure_times=["08:00", "14:00", "20:00", "23:00"],
                            is_active=True
                        )
                        db.add(route1)
                        
                        route2 = Route(
                            provider_id=provider.id,
                            from_district_id=district_map[to_district].id,
                            to_district_id=district_map[from_district].id,
                            base_fare=fare,
                            distance_km=200 + (hash(from_district + to_district) % 300),
                            duration_hours=3 + (hash(from_district + to_district) % 6),
                            seat_class="AC" if hash(provider.name) % 2 == 0 else "Non-AC",
                            available_seats=35 + (hash(to_district) % 10),
                            total_seats=40,
                            departure_times=["07:00", "13:00", "19:00", "22:00"],
                            is_active=True
                        )
                        db.add(route2)
        
        db.commit()
    db.close()

@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("static/index.html")

@app.get("/script.js")
async def get_script():
    """Serve the JavaScript file"""
    return FileResponse("static/script.js")

@app.get("/api/districts")
async def get_districts(db: Session = Depends(get_db)):
    """Get all districts"""
    districts = db.query(District).all()
    return [{"name": d.name, "dropping_points": d.dropping_points} for d in districts]

@app.get("/api/bus-providers")
async def get_bus_providers(db: Session = Depends(get_db)):
    """Get all bus providers"""
    providers = db.query(BusProvider).all()
    return [{
        "name": p.name,
        "coverage_districts": p.coverage_districts,
        "official_address": p.official_address,
        "contact_info": p.contact_info
    } for p in providers]

@app.get("/api/search-buses")
async def search_buses(
    from_district: str = Query(...),
    to_district: str = Query(...),
    max_fare: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Search for available buses between districts"""
    # Get districts
    from_dist = db.query(District).filter(District.name == from_district).first()
    to_dist = db.query(District).filter(District.name == to_district).first()
    
    if not from_dist or not to_dist:
        raise HTTPException(status_code=404, detail="District not found")
    
    # Query routes
    query = db.query(Route).filter(
        Route.from_district_id == from_dist.id,
        Route.to_district_id == to_dist.id,
        Route.is_active == True
    )
    
    if max_fare:
        query = query.filter(Route.base_fare <= max_fare)
    
    routes = query.all()
    
    # Build response
    available_buses = []
    for route in routes:
        provider = db.query(BusProvider).filter(BusProvider.id == route.provider_id).first()
        if provider and provider.is_active:
            available_buses.append({
                "provider": provider.name,
                "from_district": from_district,
                "to_district": to_district,
                "fare": route.base_fare,
                "seat_class": route.seat_class,
                "available_seats": route.available_seats,
                "total_seats": route.total_seats,
                "departure_times": route.departure_times,
                "duration_hours": route.duration_hours,
                "distance_km": route.distance_km,
                "rating": provider.rating,
                "contact": provider.contact_info
            })
    
    return available_buses

@app.post("/api/bookings", response_model=BookingResponse)
async def create_booking(booking_req: BookingRequest, db: Session = Depends(get_db)):
    """Create a new booking"""
    # Get districts and provider
    from_dist = db.query(District).filter(District.name == booking_req.from_district).first()
    to_dist = db.query(District).filter(District.name == booking_req.to_district).first()
    provider = db.query(BusProvider).filter(BusProvider.name == booking_req.bus_provider).first()
    
    if not from_dist or not to_dist or not provider:
        raise HTTPException(status_code=404, detail="District or provider not found")
    
    # Find route
    route = db.query(Route).filter(
        Route.from_district_id == from_dist.id,
        Route.to_district_id == to_dist.id,
        Route.provider_id == provider.id,
        Route.is_active == True
    ).first()
    
    # Calculate fare (base fare + dropping point fee if any)
    base_fare = route.base_fare if route else 400
    dropping_fee = 0
    if booking_req.dropping_point:
        for dp in to_dist.dropping_points:
            if dp['name'] == booking_req.dropping_point:
                dropping_fee = dp.get('price', 0)
                break
    
    total_fare = base_fare + dropping_fee
    
    booking = Booking(
        booking_reference=generate_booking_reference(),
        route_id=route.id if route else None,
        provider_id=provider.id,
        customer_name=booking_req.customer_name,
        customer_phone=booking_req.customer_phone,
        from_district=booking_req.from_district,
        to_district=booking_req.to_district,
        bus_provider=booking_req.bus_provider,
        dropping_point=booking_req.dropping_point,
        travel_date=booking_req.travel_date,
        fare=base_fare,
        total_fare=total_fare,
        num_seats=1,
        status="active",
        payment_status="pending"
    )
    
    db.add(booking)
    
    # Update available seats if route exists
    if route and route.available_seats > 0:
        route.available_seats -= 1
    
    db.commit()
    db.refresh(booking)
    
    return booking

@app.get("/api/bookings", response_model=List[BookingResponse])
async def get_bookings(
    phone: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all bookings or filter by phone number"""
    query = db.query(Booking)
    if phone:
        query = query.filter(Booking.customer_phone == phone)
    
    bookings = query.order_by(Booking.booking_date.desc()).all()
    return bookings

@app.delete("/api/bookings/{booking_reference}")
async def cancel_booking(booking_reference: str, db: Session = Depends(get_db)):
    """Cancel a booking"""
    booking = db.query(Booking).filter(Booking.booking_reference == booking_reference).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status == "cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    booking.status = "cancelled"
    db.commit()
    
    return {"message": "Booking cancelled successfully", "booking_reference": booking_reference}

@app.post("/api/rag-query")
async def rag_query(query: SearchQuery):
    """Use RAG pipeline to answer questions about bus providers"""
    results = rag_pipeline.search(query.query, top_k=3)
    
    # Format response
    response = {
        "query": query.query,
        "results": []
    }
    
    for result in results:
        contact_info = rag_pipeline.extract_contact_info(result['content'])
        response["results"].append({
            "provider": result['provider'],
            "relevance_score": result['relevance_score'],
            "contact_info": contact_info,
            "excerpt": result['content'][:500] + "..."
        })
    
    return response

@app.get("/api/provider-details/{provider_name}")
async def get_provider_details(provider_name: str, db: Session = Depends(get_db)):
    """Get detailed information about a specific bus provider using RAG"""
    # Get from database
    provider = db.query(BusProvider).filter(
        BusProvider.name.ilike(f"%{provider_name}%")
    ).first()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Get additional info from RAG
    provider_doc = rag_pipeline.get_provider_info(provider_name)
    contact_details = {}
    if provider_doc:
        contact_details = rag_pipeline.extract_contact_info(provider_doc['content'])
    
    return {
        "name": provider.name,
        "coverage_districts": provider.coverage_districts,
        "official_address": contact_details.get('address', provider.official_address),
        "contact_info": contact_details.get('phone', provider.contact_info),
        "email": contact_details.get('email', ''),
        "website": contact_details.get('website', ''),
        "privacy_policy": provider.privacy_policy
    }

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
