// Global state
let districts = [];
let busProviders = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDistricts();
    loadBusProviders();
    setMinDate();
    initMobileMenu();
});

// Mobile menu toggle
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close menu when clicking on a link
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
            });
        });
    }
}

// Set minimum date to today
function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('bookDate').setAttribute('min', today);
}

// Load districts
async function loadDistricts() {
    try {
        console.log('Loading districts...');
        const response = await fetch('/api/districts');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        districts = await response.json();
        console.log('Loaded districts:', districts);
        
        const selects = ['searchFrom', 'searchTo', 'bookFrom', 'bookTo'];
        selects.forEach(id => {
            const select = document.getElementById(id);
            if (!select) {
                console.error(`Select element not found: ${id}`);
                return;
            }
            select.innerHTML = '<option value="">Select city</option>';
            districts.forEach(district => {
                const option = document.createElement('option');
                option.value = district.name;
                option.textContent = district.name;
                select.appendChild(option);
            });
        });
        console.log('Districts loaded successfully');
    } catch (error) {
        console.error('Error loading districts:', error);
        showNotification('Failed to load districts', 'error');
    }
}

// Load bus providers
async function loadBusProviders() {
    try {
        console.log('Loading bus providers...');
        const response = await fetch('/api/bus-providers');
        console.log('Bus providers response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        busProviders = await response.json();
        console.log('Loaded bus providers:', busProviders);
        
        const select = document.getElementById('bookProvider');
        if (!select) {
            console.error('Provider select element not found');
            return;
        }
        
        select.innerHTML = '<option value="">Select bus provider</option>';
        busProviders.forEach(provider => {
            const option = document.createElement('option');
            option.value = provider.name;
            option.textContent = `${provider.name} (Rating: ${provider.rating || '4.0'}⭐)`;
            select.appendChild(option);
        });
        console.log('Bus providers loaded successfully');
    } catch (error) {
        console.error('Error loading bus providers:', error);
    }
}

// Update dropping points when destination changes
document.getElementById('bookTo')?.addEventListener('change', function() {
    const districtName = this.value;
    const district = districts.find(d => d.name === districtName);
    const droppingSelect = document.getElementById('bookDropping');
    
    if (district && district.dropping_points) {
        droppingSelect.innerHTML = '<option value="">Select dropping point</option>';
        district.dropping_points.forEach(point => {
            const option = document.createElement('option');
            option.value = point.name;
            option.textContent = `${point.name} - ৳${point.price}`;
            droppingSelect.appendChild(option);
        });
    }
});

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('tab-active');
        btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    
    // Show selected tab
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
    document.getElementById(`content-${tabName}`).classList.add('fade-in');
    
    // Add active class to button
    const activeBtn = document.getElementById(`tab-${tabName}`);
    activeBtn.classList.add('tab-active');
    activeBtn.classList.remove('bg-gray-200', 'text-gray-700');
}

// Tab switching with loader and scroll
function showTabWithLoader(tabName) {
    // Show loader
    const loader = document.getElementById('loaderOverlay');
    loader.classList.add('active');
    
    // Simulate loading delay
    setTimeout(() => {
        showTab(tabName);
        
        // Hide loader
        loader.classList.remove('active');
        
        // Scroll to main content
        const mainContent = document.getElementById('mainContent');
        mainContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Auto-load data if needed
        if (tabName === 'bookings') {
            // Auto-focus on search input
            setTimeout(() => {
                document.getElementById('searchBooking').focus();
            }, 500);
        }
    }, 800);
}

// Search buses
async function searchBuses() {
    const from = document.getElementById('searchFrom').value;
    const to = document.getElementById('searchTo').value;
    const maxFare = document.getElementById('maxFare').value;
    
    if (!from || !to) {
        showNotification('Please select both origin and destination', 'error');
        return;
    }
    
    try {
        let url = `/api/search-buses?from_district=${from}&to_district=${to}`;
        if (maxFare) url += `&max_fare=${maxFare}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        displaySearchResults(data);
    } catch (error) {
        console.error('Error searching buses:', error);
        showNotification('Failed to search buses', 'error');
    }
}

// Display search results
function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-bus-alt text-gray-300 text-6xl mb-4"></i>
                <p class="text-xl text-gray-600">No buses found for this route</p>
                <p class="text-gray-500 mt-2">Try different cities or adjust your filters</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <h3 class="text-2xl font-bold mb-4 gradient-text">
            <i class="fas fa-check-circle mr-2"></i>Found ${results.length} bus(es)
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            ${results.map(bus => `
                <div class="border-2 border-purple-200 rounded-xl p-6 card-hover bg-gradient-to-br from-white to-purple-50">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h4 class="text-xl font-bold text-purple-700">
                                <i class="fas fa-bus mr-2"></i>${bus.provider}
                            </h4>
                            <p class="text-gray-600 mt-1">
                                <i class="fas fa-route mr-2"></i>${bus.from_district} → ${bus.to_district}
                            </p>
                        </div>
                        <span class="bg-purple-600 text-white px-4 py-2 rounded-full font-bold">
                            ৳${bus.fare}
                        </span>
                    </div>
                    <div class="space-y-2 mb-4">
                        <p class="text-sm text-gray-600">
                            <i class="fas fa-chair text-purple-600 mr-2"></i>
                            Available Seats: <span class="font-semibold">${bus.available_seats || 'N/A'}</span>
                        </p>
                        <p class="text-sm text-gray-600">
                            <i class="fas fa-star text-yellow-400 mr-2"></i>
                            Rating: <span class="font-semibold">${bus.rating || '4.0'} / 5.0</span>
                        </p>
                    </div>
                    <button onclick="quickBook('${bus.provider}', '${bus.from_district}', '${bus.to_district}', ${bus.fare})" 
                            class="btn-gradient text-white px-6 py-2 rounded-lg font-semibold w-full">
                        <i class="fas fa-ticket-alt mr-2"></i>Book Now
                    </button>
                </div>
            `).join('')}
        </div>
    `;
}

// Quick book from search results
function quickBook(provider, from, to, fare) {
    showTabWithLoader('book');
    setTimeout(() => {
        document.getElementById('bookProvider').value = provider;
        document.getElementById('bookFrom').value = from;
        document.getElementById('bookTo').value = to;
        
        // Trigger change event to load dropping points
        document.getElementById('bookTo').dispatchEvent(new Event('change'));
    }, 900);
}

// Handle booking form submission
document.getElementById('bookingForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loader
    const loader = document.getElementById('loaderOverlay');
    loader.classList.add('active');
    
    const bookingData = {
        customer_name: document.getElementById('bookName').value,
        customer_phone: document.getElementById('bookPhone').value,
        from_district: document.getElementById('bookFrom').value,
        to_district: document.getElementById('bookTo').value,
        bus_provider: document.getElementById('bookProvider').value,
        travel_date: document.getElementById('bookDate').value,
        dropping_point: document.getElementById('bookDropping').value || ''
    };
    
    try {
        const response = await fetch('/api/bookings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        
        // Hide loader
        loader.classList.remove('active');
        
        if (response.ok) {
            displayBookingSuccess(result);
            document.getElementById('bookingForm').reset();
        } else {
            showNotification(result.detail || 'Booking failed', 'error');
        }
    } catch (error) {
        console.error('Error creating booking:', error);
        loader.classList.remove('active');
        showNotification('Failed to create booking', 'error');
    }
});

// Display booking success
function displayBookingSuccess(booking) {
    const container = document.getElementById('bookingResult');
    container.innerHTML = `
        <div class="bg-green-50 border-2 border-green-500 rounded-xl p-6 fade-in">
            <div class="text-center mb-4">
                <i class="fas fa-check-circle text-green-500 text-5xl mb-3"></i>
                <h3 class="text-2xl font-bold text-green-700">Booking Confirmed!</h3>
            </div>
            <div class="bg-white rounded-lg p-4 space-y-2">
                <p class="flex justify-between">
                    <span class="text-gray-600">Reference:</span>
                    <span class="font-bold text-purple-700">${booking.booking_reference}</span>
                </p>
                <p class="flex justify-between">
                    <span class="text-gray-600">Passenger:</span>
                    <span class="font-semibold">${booking.customer_name}</span>
                </p>
                <p class="flex justify-between">
                    <span class="text-gray-600">Route:</span>
                    <span class="font-semibold">${booking.from_district} → ${booking.to_district}</span>
                </p>
                <p class="flex justify-between">
                    <span class="text-gray-600">Bus:</span>
                    <span class="font-semibold">${booking.bus_provider}</span>
                </p>
                <p class="flex justify-between">
                    <span class="text-gray-600">Date:</span>
                    <span class="font-semibold">${booking.travel_date}</span>
                </p>
                <p class="flex justify-between">
                    <span class="text-gray-600">Fare:</span>
                    <span class="font-bold text-green-600">৳${booking.fare}</span>
                </p>
            </div>
            <p class="text-sm text-gray-600 mt-4 text-center">
                <i class="fas fa-info-circle mr-1"></i>
                Save your booking reference for future use
            </p>
        </div>
    `;
}

// Load bookings
async function loadBookings() {
    const search = document.getElementById('searchBooking').value.trim();
    
    try {
        const response = await fetch(`/api/bookings${search ? `?search=${search}` : ''}`);
        const bookings = await response.json();
        
        displayBookings(bookings);
    } catch (error) {
        console.error('Error loading bookings:', error);
        showNotification('Failed to load bookings', 'error');
    }
}

// Display bookings
function displayBookings(bookings) {
    const container = document.getElementById('bookingsList');
    
    if (bookings.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <i class="fas fa-ticket-alt text-gray-300 text-6xl mb-4"></i>
                <p class="text-xl text-gray-600">No bookings found</p>
                <p class="text-gray-500 mt-2">Try searching with phone number or reference</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="space-y-4">
            ${bookings.map(booking => `
                <div class="border-2 ${booking.status === 'cancelled' ? 'border-red-200 bg-red-50' : 'border-purple-200 bg-white'} rounded-xl p-6 card-hover">
                    <div class="flex justify-between items-start mb-4">
                        <div>
                            <h4 class="text-lg font-bold text-purple-700">
                                Ref: ${booking.booking_reference}
                            </h4>
                            <p class="text-sm text-gray-600">
                                <i class="fas fa-calendar mr-1"></i>
                                Booked: ${new Date(booking.booking_date).toLocaleDateString()}
                            </p>
                        </div>
                        <span class="px-3 py-1 rounded-full text-sm font-semibold ${
                            booking.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                        }">
                            ${booking.status.toUpperCase()}
                        </span>
                    </div>
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div>
                            <p class="text-sm text-gray-600">Passenger</p>
                            <p class="font-semibold">${booking.customer_name}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Phone</p>
                            <p class="font-semibold">${booking.customer_phone}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Route</p>
                            <p class="font-semibold">${booking.from_district} → ${booking.to_district}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Travel Date</p>
                            <p class="font-semibold">${booking.travel_date}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Bus Provider</p>
                            <p class="font-semibold">${booking.bus_provider}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Fare</p>
                            <p class="font-bold text-purple-700">৳${booking.fare}</p>
                        </div>
                    </div>
                    ${booking.status === 'active' ? `
                        <button onclick="cancelBooking('${booking.booking_reference}')" 
                                class="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-semibold transition">
                            <i class="fas fa-times-circle mr-2"></i>Cancel Booking
                        </button>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

// Cancel booking
async function cancelBooking(reference) {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    
    try {
        const response = await fetch(`/api/bookings/${reference}/cancel`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Booking cancelled successfully', 'success');
            loadBookings();
        } else {
            showNotification('Failed to cancel booking', 'error');
        }
    } catch (error) {
        console.error('Error cancelling booking:', error);
        showNotification('Failed to cancel booking', 'error');
    }
}

// Ask RAG
async function askRAG() {
    const question = document.getElementById('ragQuestion').value.trim();
    
    if (!question) {
        showNotification('Please enter a question', 'error');
        return;
    }
    
    const answerContainer = document.getElementById('ragAnswer');
    answerContainer.innerHTML = `
        <div class="bg-purple-50 border-2 border-purple-200 rounded-xl p-6 text-center">
            <i class="fas fa-spinner fa-spin text-purple-600 text-3xl mb-3"></i>
            <p class="text-purple-700">AI is thinking...</p>
        </div>
    `;
    
    try {
        const response = await fetch('/api/rag-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: question })
        });
        
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            let answerHTML = `
                <div class="bg-gradient-to-br from-purple-50 to-blue-50 border-2 border-purple-300 rounded-xl p-6 fade-in">
                    <div class="flex items-start space-x-4">
                        <i class="fas fa-robot text-purple-600 text-3xl"></i>
                        <div class="flex-1">
                            <h4 class="text-lg font-bold text-purple-700 mb-3">AI Assistant Response:</h4>
            `;
            
            data.results.forEach((result, index) => {
                answerHTML += `
                    <div class="bg-white rounded-lg p-4 mb-4 shadow-sm">
                        <h5 class="font-bold text-purple-600 mb-2">
                            <i class="fas fa-bus mr-2"></i>${result.provider}
                        </h5>
                        ${result.contact_info ? `
                            <div class="mb-3">
                                <p class="text-sm font-semibold text-gray-700 mb-1">Contact Information:</p>
                                <div class="text-sm text-gray-600 space-y-1">
                                    ${result.contact_info.phone ? `<p><i class="fas fa-phone mr-2 text-purple-500"></i>${result.contact_info.phone}</p>` : ''}
                                    ${result.contact_info.email ? `<p><i class="fas fa-envelope mr-2 text-purple-500"></i>${result.contact_info.email}</p>` : ''}
                                    ${result.contact_info.website ? `<p><i class="fas fa-globe mr-2 text-purple-500"></i>${result.contact_info.website}</p>` : ''}
                                    ${result.contact_info.address ? `<p><i class="fas fa-map-marker-alt mr-2 text-purple-500"></i>${result.contact_info.address}</p>` : ''}
                                </div>
                            </div>
                        ` : ''}
                        <p class="text-sm text-gray-600">${result.excerpt}</p>
                        <p class="text-xs text-gray-400 mt-2">Relevance: ${(result.relevance_score * 100).toFixed(1)}%</p>
                    </div>
                `;
            });
            
            answerHTML += `
                        </div>
                    </div>
                </div>
            `;
            
            answerContainer.innerHTML = answerHTML;
        } else {
            answerContainer.innerHTML = `
                <div class="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-6">
                    <p class="text-yellow-700"><i class="fas fa-info-circle mr-2"></i>No relevant information found. Try asking about specific bus providers like Hanif, Green Line, or Shyamoli.</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error asking RAG:', error);
        answerContainer.innerHTML = `
            <div class="bg-red-50 border-2 border-red-300 rounded-xl p-6">
                <p class="text-red-700"><i class="fas fa-exclamation-circle mr-2"></i>Failed to get answer. Please try again.</p>
            </div>
        `;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-blue-500'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-6 ${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg z-50 fade-in`;
    notification.innerHTML = `
        <div class="flex items-center space-x-3">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} text-xl"></i>
            <span class="font-semibold">${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}
