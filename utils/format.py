import urllib


def format_monument_info(monument_info: dict) -> str:
    formatted_info = f"""
### {monument_info.get('name', 'N/A')}

**Location:** {monument_info.get('location', 'N/A')}

**Introduction:** {monument_info.get('intro', 'N/A')}

**History and Construction:** {monument_info.get('history', 'N/A')}

**Historical Events** {monument_info.get('historical_events', 'N/A')}

**Significance:** {monument_info.get('significance', 'N/A')}

**Visitor Info:** {monument_info.get('visitor_info', 'N/A')}

Here you can view the 3D model of [{monument_info.get('name', 'N/A')}](http://192.168.11.121:8080)

**Nearby Places:**
"""

    starting_point_encoded = urllib.parse.quote_plus(monument_info.get("name", ""))
    for place, info in monument_info.get("nearby_places", {}).items():
        destination_encoded = urllib.parse.quote_plus(place)
        place_info = info if info else "Click for location"
        formatted_info += f"- [{place}](https://www.google.com/maps/dir/{starting_point_encoded}/{destination_encoded}) : {info} \n"
    return formatted_info