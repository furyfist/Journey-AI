"""Reusable fixture data for Unsplash photo tests."""

# A realistic minimal Unsplash search/photos response containing one result.
UNSPLASH_SEARCH_RESPONSE_ONE_RESULT = {
    "total": 1,
    "total_pages": 1,
    "results": [
        {
            "id": "abc123",
            "description": "Tokyo skyline at dusk",
            "alt_description": "Tokyo skyline at dusk with Mount Fuji in the background",
            "urls": {
                "full": "https://images.unsplash.com/photo-abc123?fit=max",
                "regular": "https://images.unsplash.com/photo-abc123?w=1080",
                "small": "https://images.unsplash.com/photo-abc123?w=400",
                "thumb": "https://images.unsplash.com/photo-abc123?w=200",
            },
            "links": {
                "html": "https://unsplash.com/photos/abc123",
            },
            "user": {
                "name": "Jane Photographer",
                "links": {
                    "html": "https://unsplash.com/@janephotographer",
                },
            },
        }
    ],
}

# Response where results list is empty — triggers fallback behaviour.
UNSPLASH_SEARCH_RESPONSE_EMPTY = {
    "total": 0,
    "total_pages": 0,
    "results": [],
}

# Response where the first result has no usable URL — also triggers fallback.
UNSPLASH_SEARCH_RESPONSE_NO_URL = {
    "total": 1,
    "total_pages": 1,
    "results": [
        {
            "id": "xyz999",
            "description": None,
            "alt_description": None,
            "urls": {},
            "links": {},
            "user": {"name": "Ghost User", "links": {}},
        }
    ],
}
