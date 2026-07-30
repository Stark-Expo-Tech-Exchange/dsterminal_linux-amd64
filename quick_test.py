import requests

# Test the new public repository
repo = "Stark-Expo-Tech-Exchange/DSTerminal-Updates-Test"
url = f"https://api.github.com/repos/{repo}/releases"

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'DSTerminal-Test'
}

print(f"Testing repository: {repo}")
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✓ Repository found!")
    print(f"Releases: {len(data)}")
    if data:
        print(f"Latest release: {data[0].get('tag_name')}")
        assets = data[0].get('assets', [])
        if assets:
            print(f"Assets: {len(assets)}")
            for asset in assets:
                print(f"  - {asset.get('name')} ({asset.get('size')} bytes)")
else:
    print(f"✗ Error: {response.status_code}")