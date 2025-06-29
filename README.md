# Festival Simulator

A comprehensive festival simulation game where you can create and manage your own music festival! Hire artists, manage the economy, handle marketing, coordinate vendors, sell tickets, design festival layouts, and create schedules while dealing with dynamic events.

## Features

### Core Gameplay
- **Artist Management**: Hire different types of artists with varying popularity, genres, and demands
- **Economic System**: Manage budget, ticket sales, vendor fees, and artist payments
- **Marketing Campaigns**: Invest in different marketing strategies to boost ticket sales
- **Vendor Management**: Coordinate food, merchandise, and service vendors
- **Festival Layout Design**: Create custom festival maps with stages, vendors, and amenities
- **Schedule Creation**: Plan artist performances and manage time slots
- **Dynamic Events**: Handle unexpected situations like artist cancellations or special requests

### Game Systems
- Real-time simulation with day/night cycles
- Dynamic pricing based on demand and supply
- Weather effects on attendance and costs
- Artist reputation and fan base simulation
- Vendor satisfaction and performance tracking
- Marketing effectiveness tracking
- Budget management and financial reporting

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd festivalsim
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Run the game:
```bash
python app.py
```

6. Open your browser and navigate to `http://localhost:5000`

## Game Controls

- **Dashboard**: Overview of your festival status, budget, and key metrics
- **Artists**: Browse and hire artists, manage contracts and special requests
- **Marketing**: Invest in advertising campaigns and track effectiveness
- **Vendors**: Manage food, merchandise, and service vendors
- **Layout**: Design your festival map with drag-and-drop interface
- **Schedule**: Create and manage the festival schedule
- **Economy**: Monitor finances, ticket sales, and revenue projections

## Game Mechanics

### Starting a Festival
1. Choose your festival location and date
2. Set your initial budget
3. Start hiring artists and vendors
4. Design your festival layout
5. Create your schedule
6. Launch marketing campaigns
7. Sell tickets and manage the event

### Winning Conditions
- Achieve target attendance numbers
- Maintain positive profit margins
- Keep artist and vendor satisfaction high
- Successfully handle dynamic events
- Create a memorable festival experience

## Contributing

Feel free to contribute to this project by:
- Reporting bugs
- Suggesting new features
- Improving the UI/UX
- Adding new artist types or vendor categories
- Enhancing the simulation algorithms

## License

This project is licensed under the MIT License. 