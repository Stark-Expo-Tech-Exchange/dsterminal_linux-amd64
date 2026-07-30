# whoami.py
import requests

# Try to get your user info
url = "https://api.github.com/user"

# Try with different possible usernames
possible_usernames = [
    "Stark-Expo-Tech-Exchange",
    "stark-expo-tech-exchange",
    "StarkExpoTechExchange"
]

for username in possible_usernames:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers={'User-Agent': 'Test'})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found user: {data['login']}")
        print(f"   Name: {data.get('name', 'N/A')}")
        print(f"   Public repos: {data['public_repos']}")
        print(f"   URL: {data['html_url']}")
        print()
    else:
        print(f"❌ {username} - Not found")