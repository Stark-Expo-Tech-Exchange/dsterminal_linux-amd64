# test_release.py
import requests

GITHUB_TOKEN = "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"
REPO = "Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'DSTerminal-Test',
    'Authorization': f'token {GITHUB_TOKEN}'
}

# Check releases
url = f"https://api.github.com/repos/{REPO}/releases"
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    releases = response.json()
    print(f"Found {len(releases)} release(s)")
    for rel in releases:
        print(f"\n📦 {rel['name']}")
        print(f"   Tag: {rel['tag_name']}")
        print(f"   Published: {rel['published_at'][:10]}")
        print(f"   Draft: {rel['draft']}")
        print(f"   Prerelease: {rel['prerelease']}")
        assets = rel.get('assets', [])
        if assets:
            print(f"   Assets: {len(assets)}")
            for asset in assets:
                print(f"     📄 {asset['name']} ({asset['size']} bytes)")
                print(f"        URL: {asset['browser_download_url'][:80]}...")
        else:
            print("   ⚠️ No assets attached")
else:
    print(f"Error: {response.status_code}")
    print(response.text)