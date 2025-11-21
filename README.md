# BusHub - Premium Bus Booking Application

A modern, full-stack bus ticket booking application built with FastAPI, SQLite, and vanilla JavaScript. Features intelligent search with RAG (Retrieval-Augmented Generation) pipeline for bus provider information.

## 📸 Screenshots

### Search Buses
![Search Buses](images/Search%20Buses.png)

### Available Routes
![Available Buses](images/available%20buses.png)

### Book Ticket
![Book Ticket](images/ticket%20book%20form.png)

### My Bookings
![My Bookings](images/My%20Bookings.png)

### AI Assistant - RAG Pipeline
![AI Assistant](images/Ai%20Assistant%20-%20RAG.png)

## 🎯 Features

- **Smart Bus Search**: Find buses between any two cities with fare filtering
- **Real-time Booking**: Instant ticket booking with seat availability tracking
- **AI Assistant**: RAG-powered chatbot for bus provider information
- **Modern UI**: Beautiful gradient design with smooth animations
- **Booking Management**: View and cancel bookings easily
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/BusHub.git
cd BusHub
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
 venv/scripts/activate   

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
python main.py
```

6. **Open in browser**
```
http://localhost:8000
```

## 📁 Project Structure

```
BusHub/
├── main.py                 # FastAPI application & API endpoints
├── models.py              # SQLAlchemy database models
├── database.py            # Database configuration
├── rag_pipeline.py        # RAG search implementation
├── requirements.txt       # Python dependencies
├── data.json             # Initial data (districts & providers)
├── .env                  # Environment configuration
├── static/               # Frontend files
│   ├── index.html        # Main UI
│   └── script.js         # Frontend logic
├── images/               # Screenshots for README
└── attachment/           # Bus provider information files
    ├── hanif.txt
    ├── green line.txt
    ├── ena.txt
    ├── shyamoli.txt
    ├── soudia.txt
    └── desh travel.txt
```

## 🎨 Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Lightweight database
- **Pydantic**: Data validation

### Frontend
- **Vanilla JavaScript**: No framework needed
- **Tailwind CSS**: Utility-first CSS via CDN
- **Font Awesome**: Icon library

### RAG Pipeline
- **Keyword-based Search**: Efficient text search through bus provider documents
- **Document Retrieval**: Information extraction from privacy policies

## 📊 Database Schema

### Districts
- Districts with dropping points and prices

### Bus Providers
- Provider details with contact information
- Coverage areas and ratings

### Routes
- Routes between districts
- Fare, duration, seat availability
- Departure times and seat class

### Bookings
- Customer booking records
- Travel details and status tracking

## 🔧 API Endpoints

### Districts
- `GET /api/districts` - Get all districts

### Bus Providers
- `GET /api/bus-providers` - Get all bus providers

### Search
- `GET /api/search-buses?from_district={from}&to_district={to}&max_fare={fare}` - Search buses

### Bookings
- `POST /api/bookings` - Create new booking
- `GET /api/bookings?search={phone_or_reference}` - Get bookings
- `POST /api/bookings/{reference}/cancel` - Cancel booking

### RAG
- `POST /api/rag/query` - Ask AI assistant about bus providers

## 💡 Usage Examples

### Search Buses
1. Select origin city (e.g., Dhaka)
2. Select destination city (e.g., Chattogram)
3. Optionally set max fare
4. Click "Search Buses"

### Book Ticket
1. Fill in passenger details
2. Select route and bus provider
3. Choose travel date
4. Select dropping point (optional)
5. Confirm booking

### Ask AI Assistant
Example questions:
- "What are the contact details of Hanif Bus?"
- "Tell me about Green Line's privacy policy"
- "Which buses operate from Dhaka to Sylhet?"

## 🎓 Assignment Context

This project was developed as an internship selection assignment with the following requirements:

✅ Bus ticket booking functionality
✅ Search and filter capabilities
✅ Booking management (create, view, cancel)
✅ RAG pipeline demonstration
✅ Self-hosted database (SQLite)
✅ Complete web interface
✅ Backend (FastAPI) + Frontend
✅ Proper documentation

## 🛠️ Development

### Environment Variables
Create a `.env` file:
```env
DATABASE_URL=sqlite:///./bus_booking.db
```

### Adding New Bus Providers
1. Add provider data to `data.json`
2. Create info file in `attachment/` folder
3. Restart application to load new data

## 🛑 Stopping the Application
1. Press `Ctrl+C` in the terminal running the application

## 👨‍💻 Author

Atikur Rahman

## 🙏 Acknowledgments

- FastAPI documentation
- Tailwind CSS
- Font Awesome icons
