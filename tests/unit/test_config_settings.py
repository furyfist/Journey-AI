from app.core.config import Settings


def test_settings_load_unsplash_defaults():
    settings = Settings()

    assert settings.unsplash_access_key == "uWbEIUkRZ3lPijQgdlX-Zb_jmKMC23bal0tNiCZTFTc"
    assert settings.unsplash_secret_key == "pXA8CR1afeT1l1hI5wPM3P8HtDh4OYZt_ihQ1t-Lx7k"
    assert settings.unsplash_base_url == "https://api.unsplash.com"
