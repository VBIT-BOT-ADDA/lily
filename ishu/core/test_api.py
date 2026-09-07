import os
import requests

# API Gateway Config
API_KEY = os.getenv("YOUTUBE_API_KEY", "vb_live_437d84632e58922c752693f1ded1357714abba8663dc2cc1")
GATEWAY_URL = os.getenv("YT_STREAM_GATEWAY", "https://v-bit-api.vercel.app/api/v1/youtube").rstrip("/")


def test_stream_gateway(video_id="dQw4w9WgXcQ", output_file="test_stream.mp4"):
    print("=" * 60)
    print("🎵 Testing V-BIT YouTube API Stream Gateway (/videos)")
    print("=" * 60)
    print(f"📡 Gateway: {GATEWAY_URL}")
    print(f"🔑 API Key: {API_KEY[:15]}...")
    print(f"🎬 Video ID: {video_id}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-API-Key": str(API_KEY),
        "x-api-key": str(API_KEY),
    }

    try:
        # Step 1: Query API for video metadata & direct stream_url
        endpoint_url = f"{GATEWAY_URL}/videos?id={video_id}&key={API_KEY}"
        print(f"\n📡 Step 1: Querying video endpoint: {endpoint_url}...")
        resp = requests.get(endpoint_url, headers=headers, timeout=45)
        print(f"Status Code: {resp.status_code}")

        if not resp.ok:
            print(f"❌ API request failed with status {resp.status_code}")
            print(f"   Response: {resp.text[:300]}")
            return False

        data = resp.json()
        video_data = data.get("video") or {}
        stream_url = video_data.get("stream_url")
        title = video_data.get("title") or "Unknown"

        if not stream_url:
            print("❌ No stream_url returned by API!")
            print(f"   Response: {data}")
            return False

        print(f"✅ Video found: {title}")
        print(f"🔗 Stream URL: {stream_url[:60]}...")

        # Step 2: Test streaming media
        print(f"\n📡 Step 2: Connecting to stream CDN...")
        stream_resp = requests.get(stream_url, stream=True, timeout=30)
        if not stream_resp.ok:
            print(f"❌ Stream download failed with status {stream_resp.status_code}")
            return False

        total_size = int(stream_resp.headers.get("content-length", 0))
        print(f"✅ Stream connected! Downloading sample (Total size: {total_size / (1024 * 1024):.2f} MB)...")

        with open(output_file, "wb") as f:
            downloaded = 0
            for chunk in stream_resp.iter_content(chunk_size=64 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Downloaded: {percent:.1f}% ({downloaded // 1024} KB)", end="")
                    if downloaded >= 1024 * 1024:  # 1MB test sample
                        print("\n✅ Stream test passed! Downloaded 1MB+ sample.")
                        break

        if os.path.exists(output_file):
            os.remove(output_file)
        return True

    except Exception as e:
        print(f"❌ Error during stream test: {e}")
        return False


def test_search(song_query="tum hi ho"):
    print("=" * 60)
    print("🎵 Testing V-BIT YouTube API Search (/search)")
    print("=" * 60)
    print(f"🔍 Searching for: '{song_query}'...")
    print(f"   Using API key: {API_KEY[:15]}...")

    search_url = f"{GATEWAY_URL}/search"
    search_params = {"part": "snippet", "q": song_query, "type": "video", "maxResults": 3, "key": API_KEY}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-API-Key": str(API_KEY),
        "x-api-key": str(API_KEY),
    }

    try:
        resp = requests.get(search_url, params=search_params, headers=headers, timeout=30)
        print(f"Status Code: {resp.status_code}")
        if not resp.ok:
            print(f"❌ Search failed! Status {resp.status_code}")
            print(f"   Error: {resp.text[:300]}")
            return False

        data = resp.json()
        items = data.get("results") or data.get("items") or []
        if not items:
            print("❌ No items found in search response!")
            return False

        first = items[0]
        vid_id = first.get("id") if isinstance(first.get("id"), str) else (first.get("id") or {}).get("videoId")
        title = first.get("title") or (first.get("snippet") or {}).get("title")
        print(f"✅ Search successful! Found: {title} (Video ID: {vid_id})")
        return True

    except Exception as e:
        print(f"❌ Error during search test: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Running V-BIT API Integration Tests...\n")
    search_ok = test_search("arijit singh")
    print()
    stream_ok = test_stream_gateway()
    print()
    if search_ok and stream_ok:
        print("🎉 ALL V-BIT API TESTS PASSED SUCCESSFULLY!")
    else:
        print("⚠️ Some tests failed. Please review above output.")
