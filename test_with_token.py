import requests

# Your GitHub token (replace with your actual token)
GITHUB_TOKEN = "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"  # Replace this!

repo = "Stark-Expo-Tech-Exchange/DSTerminal_releases_latest"

headers = {
    'Accept': 'application/vnd.github.v3+json',
    'User-Agent': 'DSTerminal-Test',
    'Authorization': f'token {GITHUB_TOKEN}'
}

print(f"Testing repository: {repo}")
print("=" * 50)

# Test 1: Check if repository exists
url = f"https://api.github.com/repos/{repo}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Repository exists!")
    print(f"   Name: {data['name']}")
    print(f"   Private: {data['private']}")
    print(f"   Default branch: {data['default_branch']}")
    
    # Test 2: Check releases
    releases_url = f"https://api.github.com/repos/{repo}/releases"
    releases_response = requests.get(releases_url, headers=headers)
    
    if releases_response.status_code == 200:
        releases = releases_response.json()
        if releases:
            print(f"\n✅ Found {len(releases)} release(s)")
            latest = releases[0]
            print(f"   Latest version: {latest['tag_name']}")
            print(f"   Published: {latest['published_at'][:10]}")
            
            assets = latest.get('assets', [])
            if assets:
                print(f"   Assets: {len(assets)}")
                for asset in assets:
                    print(f"     📦 {asset['name']} ({asset['size']} bytes)")
            else:
                print("   ⚠️ No assets in this release")
        else:
            print("⚠️ No releases found")
    else:
        print(f"⚠️ Could not fetch releases: {releases_response.status_code}")
        
elif response.status_code == 404:
    print(f"❌ Repository not found (404)")
    print("   The repository doesn't exist or you don't have access")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)