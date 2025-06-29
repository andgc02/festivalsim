#!/usr/bin/env python3
"""
Simple test script to verify API endpoints work correctly
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_api_endpoint(endpoint, method='GET', data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        else:
            print(f"Unsupported method: {method}")
            return False
            
        print(f"\n=== Testing {method} {endpoint} ===")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print(f"Response: {json.dumps(json_data, indent=2)[:500]}...")
                return True
            except json.JSONDecodeError:
                print(f"Response is not JSON: {response.text[:200]}...")
                return False
        else:
            print(f"Error response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"Connection error: Make sure Flask app is running on {BASE_URL}")
        return False
    except Exception as e:
        print(f"Error testing {endpoint}: {e}")
        return False

def test_interactive_events():
    """Test the interactive events functionality"""
    print("Testing Interactive Events...")
    
    # Test force generate events
    print("\n1. Force generating events...")
    response = requests.post(f'{BASE_URL}/api/events/force_generate/1')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Generated {data['events_generated']} events")
        if data['events']:
            event = data['events'][0]
            print(f"   Sample event: {event['type']} - {event['description']}")
            if event.get('interactive_options'):
                print(f"   Has {len(event['interactive_options'])} interactive options")
    else:
        print(f"❌ Failed to generate events: {response.status_code}")
    
    # Test event response (if we have events)
    print("\n2. Testing event response...")
    response = requests.post(f'{BASE_URL}/api/events/respond/1', json={
        'event_type': 'Technical Issues',
        'option_id': 'call_backup'
    })
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Event response successful: {data['message']}")
        print(f"   Cost: ${data['cost']}")
        print(f"   New budget: ${data['new_budget']}")
    else:
        print(f"❌ Event response failed: {response.status_code} - {response.text}")

def main():
    """Run API tests"""
    print("Festival Simulator API Test")
    print("=" * 40)
    
    # Test basic endpoints
    endpoints_to_test = [
        ('/api/artists', 'GET'),
        ('/api/vendors', 'GET'),
        ('/api/marketing/campaigns', 'GET'),
        ('/api/festival/1', 'GET'),
    ]
    
    success_count = 0
    total_count = len(endpoints_to_test)
    
    for endpoint, method in endpoints_to_test:
        if test_api_endpoint(endpoint, method):
            success_count += 1
    
    print(f"\n{'=' * 40}")
    print(f"Test Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("✅ All API endpoints are working correctly!")
    else:
        print("❌ Some API endpoints are not working. Check the Flask app.")

if __name__ == '__main__':
    test_interactive_events() 