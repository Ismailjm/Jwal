from io import BytesIO
import httpx

async def text_to_speech(text):
    CHUNK_SIZE = 1024
    ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
    ELEVENLABS_API_KEY = "sk_8a7dd5a2f0bad8fccd7fcd737e96fd46f262e79e675a5c0f"
    mime_type = "audio/mpeg"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
    "Accept": mime_type,
    "Content-Type": "application/json",
    "xi-api-key": ELEVENLABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.post(url, json=data, headers=headers)
        response.raise_for_status()  # Ensure we notice bad responses

        buffer = BytesIO()
        buffer.name = f"output_audio.{mime_type.split('/')[1]}"

        async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
            if chunk:
                buffer.write(chunk)
        
        buffer.seek(0)
        return buffer.name, buffer.read()