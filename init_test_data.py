"""
Initialize Test Data
Clears all tickets and generates 7 random test tickets
Run this after starting the backend
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def clear_and_generate_test_data():
    """Clear all tickets and generate test data"""
    
    print("🧹 Clearing all existing tickets...")
    try:
        response = requests.delete(f"{BASE_URL}/api/tickets/clear-all")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Deleted {data['deleted_count']} ticket(s)")
        else:
            print(f"⚠️  Clear tickets returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to clear tickets: {e}")
        print("Make sure the backend is running on http://localhost:8000")
        return
    
    # Wait a moment
    time.sleep(1)
    
    print("\n🎲 Generating 7 random test tickets...")
    try:
        response = requests.post(f"{BASE_URL}/api/tickets/generate-test-tickets?count=7")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created {data['count']} test ticket(s)")
            print("\nGenerated Tickets:")
            for ticket in data['tickets']:
                print(f"  • {ticket['ticket_id']}: {ticket['subject'][:50]}...")
                print(f"    Category: {ticket['category']}, Severity: {ticket['severity']}")
        else:
            print(f"⚠️  Generate tickets returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to generate tickets: {e}")
        return
    
    print("\n✨ Test data initialization complete!")
    print("📊 Open http://localhost:5173 to view the dashboard")

if __name__ == "__main__":
    clear_and_generate_test_data()
