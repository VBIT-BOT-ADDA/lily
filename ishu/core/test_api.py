
import requests
import os

# API Gateway Config
API_KEY = os.getenv("YOUTUBE_API_KEY", "v-bit-free-YOUR_UNIQUE_API_KEY")
GATEWAY_URL = os.getenv("YT_STREAM_GATEWAY", "https://vbit-api-store.vercel.app/api/v1/yt")


def test_stream_gateway(video_id="dQw4w9WgXcQ", output_file="test_stream.mp3"):
    print("=" * 60)
    print("🎵 Testing YouTube Stream Gateway (/play/audio)")
    print("=" * 60)
    print(f"📡 Gateway: {GATEWAY_URL}")
    print(f"🔑 API Key: {API_KEY[:15]}...")
    print(f"🎬 Video ID: {video_id}")

    stream_url = f"{GATEWAY_URL}/play/audio?id={video_id}&api_key={API_KEY}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-API-Key": str(API_KEY),
    }

    try:
        print(f"\n📡 Connecting to stream endpoint: {stream_url}...")
        resp = requests.get(stream_url, headers=headers, stream=True, timeout=30)
        print(f"Status Code: {resp.status_code}")

        if not resp.ok:
            print(f"❌ Request failed with status {resp.status_code}")
            print(f"   Response: {resp.text[:300]}")
            return False

        total_size = int(resp.headers.get("content-length", 0))
        print(f"✅ Connection successful! Downloading to {output_file} (Size: {total_size / (1024 * 1024):.2f} MB)...")

        with open(output_file, "wb") as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=64 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Downloaded: {percent:.1f}% ({downloaded // 1024} KB)", end="")
                    if downloaded > 1024 * 1024:  # 1MB test sample
                        print("\n✅ Stream test passed! Downloaded 1MB+ sample.")
                        break

        if os.path.exists(output_file):
            os.remove(output_file)
        return True

    except Exception as e:
        print(f"❌ Error during stream test: {e}")
        return False


def download_song(song_query="tum hi ho", output_file="downloaded_song.mp3"):
    print("=" * 60)
    print("🎵 Song Downloader via YouTube API Proxy")
    print("=" * 60)
    print(f"🔍 Searching for: '{song_query}'...")
    print(f"   Using API key: {API_KEY[:15]}...")

    # First search for the song
    search_params = {"api_key": API_KEY, "q": song_query}
    headers = {"X-API-Key": str(API_KEY)}

    try:
        print(f"\n📡 Step 1: Sending search request...")
        search_response = requests.get(
            f"{GATEWAY_URL}/search",
            params=search_params,
            headers=headers,
            timeout=30
        )

        if not search_response.ok:
            print(f"❌ Search failed! Status {search_response.status_code}")
            print(f"   Error: {search_response.text}")
            return False

        search_data = search_response.json()
        if not search_data.get("results") or len(search_data["results"]) == 0:
            print("❌ No songs found!")
            return False
            
        video_id = search_data["results"][0]["id"]
        title = search_data["results"][0]["title"]
        print(f"✅ Search successful! Found: {title} (ID: {video_id})")

        # Now try to get audio (using /audio endpoint)
        audio_params = {
            "api_key": API_KEY,
            "id": video_id,
        }

        print(f"\n📡 Step 2: Getting audio stream URL...")
        audio_metadata_response = requests.get(
            f"{GATEWAY_URL}/audio",
            params=audio_params,
            headers=headers,
            timeout=60
        )

        if not audio_metadata_response.ok:
            print(f"❌ Audio metadata failed! Status {audio_metadata_response.status_code}")
            print(f"   Error: {audio_metadata_response.text[:500]}")
            return False

        audio_data = audio_metadata_response.json()
        if "audio" not in audio_data or "best_audio" not in audio_data["audio"] or "url" not in audio_data["audio"]["best_audio"]:
            print("❌ Failed to find audio stream URL in the response!")
            return False

        stream_url = audio_data["audio"]["best_audio"]["url"]
        
        print(f"\n📡 Step 3: Downloading audio stream...")
        audio_response = requests.get(
            stream_url,
            stream=True,
            timeout=60
        )

        if audio_response.ok:
            total_size = int(audio_response.headers.get('content-length', 0))
            print(f"✅ Starting download to {output_file} (size: {total_size / 1024 / 1024:.2f} MB)...")

            with open(output_file, 'wb') as f:
                downloaded = 0
                for chunk in audio_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r   Downloaded: {percent:.1f}%", end='')

            print(f"\n✅ Download complete! File saved as: {os.path.abspath(output_file)}")
            print("=" * 60)
            return True
        else:
            print(f"❌ Audio download failed! Status {audio_response.status_code}")
            print(f"   Error: {audio_response.text[:500]}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_stream_gateway()
