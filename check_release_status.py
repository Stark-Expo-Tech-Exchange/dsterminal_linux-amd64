#!python
# check_release_status.py
import requests

GITHUB_TOKEN = "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"
REPO = "Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'DSTerminal-Test',
    'Authorization': f'token {GITHUB_TOKEN}'
}

print("Checking release status...")
print("=" * 50)

# Check if the release exists via the tag
tag = "v4.0.0.113"
url = f"https://api.github.com/repos/{REPO}/releases/tags/{tag}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    release = response.json()
    print(f"âœ… Release found!")
    print(f"   Name: {release.get('name', 'N/A')}")
    print(f"   Draft: {release.get('draft', 'N/A')}")
    print(f"   Prerelease: {release.get('prerelease', 'N/A')}")
    print(f"   Published: {release.get('published_at', 'N/A')}")
    assets = release.get('assets', [])
    print(f"   Assets: {len(assets)}")
    for asset in assets:
        print(f"     ðŸ“¦ {asset['name']} ({asset['size']} bytes)")
        print(f"        URL: {asset['browser_download_url']}")
else:
    print(f"âŒ Release not found: {response.status_code}")
    
    # Check all releases
    print("\nChecking all releases...")
    all_url = f"https://api.github.com/repos/{REPO}/releases"
    all_response = requests.get(all_url, headers=headers)
    
    if all_response.status_code == 200:
        releases = all_response.json()
        print(f"Found {len(releases)} release(s)")
        for rel in releases:
            print(f"  - {rel['tag_name']}: {rel['name']} (Draft: {rel['draft']}, Prerelease: {rel['prerelease']})")
    else:
        print(f"Error: {all_response.status_code}")
        print(all_response.text)