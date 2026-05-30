from app.photos.schemas import PhotoResult, PhotoSearchQuery


def test_photo_search_query_requires_non_empty_text():
    query = PhotoSearchQuery(query="Tokyo skyline")

    assert query.query == "Tokyo skyline"


def test_photo_result_allows_unsplash_payload():
    result = PhotoResult(
        query="Tokyo skyline",
        image_url="https://images.unsplash.com/photo-123",
        thumb_url="https://images.unsplash.com/thumb-123",
        alt_text="Tokyo skyline at dusk",
        photographer_name="Jane Doe",
        photographer_url="https://unsplash.com/@janedoe",
        unsplash_page_url="https://unsplash.com/photos/example",
        source="unsplash",
    )

    assert result.query == "Tokyo skyline"
    assert str(result.image_url) == "https://images.unsplash.com/photo-123"
    assert result.source == "unsplash"


def test_photo_result_defaults_to_fallback_when_image_missing():
    result = PhotoResult(query="Unknown destination")

    assert result.image_url is None
    assert result.source == "fallback"
