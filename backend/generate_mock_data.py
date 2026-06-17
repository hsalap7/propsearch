import csv
import random
import os

localities = [
    {"name": "HSR Layout", "lat": 12.9121, "lng": 77.6446, "base_price": 8000, "base_area": 1200},
    {"name": "Whitefield", "lat": 12.9698, "lng": 77.7499, "base_price": 7500, "base_area": 1400},
    {"name": "Koramangala", "lat": 12.9352, "lng": 77.6245, "base_price": 9500, "base_area": 1100},
    {"name": "Indiranagar", "lat": 12.9719, "lng": 77.6412, "base_price": 10500, "base_area": 1300},
    {"name": "Electronic City", "lat": 12.8452, "lng": 77.6602, "base_price": 5500, "base_area": 1000},
    {"name": "Marathahalli", "lat": 12.9569, "lng": 77.7011, "base_price": 6500, "base_area": 1200},
    {"name": "Bellandur", "lat": 12.9304, "lng": 77.6784, "base_price": 7200, "base_area": 1350},
    {"name": "Sarjapur", "lat": 12.9226, "lng": 77.6750, "base_price": 6800, "base_area": 1250},
    {"name": "Hebbal", "lat": 13.0354, "lng": 77.5988, "base_price": 8200, "base_area": 1450},
    {"name": "Jayanagar", "lat": 12.9299, "lng": 77.5824, "base_price": 9000, "base_area": 1150},
]

def generate_csv(filename: str, num_records: int = 1000, update_records: bool = False):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "property_type", "price", "area_sqft", "bedrooms", "address", "locality", "city", "latitude", "longitude"])
        
        for i in range(1, num_records + 1):
            loc = random.choice(localities)
            area = int(random.normalvariate(loc["base_area"], 200))
            if area < 500: area = 500
            
            # Apply a discount or markup if this is an update pass
            price_multiplier = random.uniform(0.9, 1.1) if update_records and random.random() < 0.3 else 1.0
            
            price_per_sqft = int(random.normalvariate(loc["base_price"], 500) * price_multiplier)
            price = area * price_per_sqft
            
            lat = loc["lat"] + random.uniform(-0.015, 0.015)
            lng = loc["lng"] + random.uniform(-0.015, 0.015)
            
            bedrooms = max(1, min(5, round(area / 400)))
            
            title = f"{bedrooms} BHK Apartment in {loc['name']}"
            
            writer.writerow([
                f"prop_{i}",
                title,
                "apartment",
                price,
                area,
                bedrooms,
                f"Random Street, {loc['name']}",
                loc['name'],
                "Bangalore",
                round(lat, 6),
                round(lng, 6)
            ])
            
    print(f"Generated {filename} with {num_records} records.")

if __name__ == "__main__":
    generate_csv("bangalore_1000.csv", 1000, False)
    # Generate a second file representing an update from the broker 2 days later (30% prices changed)
    generate_csv("bangalore_1000_updated.csv", 1000, True)
