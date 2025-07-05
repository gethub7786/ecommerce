from .api_keystone import app  # Keystone routes registered here

# Import other supplier APIs so their routes attach to shared app and suppliers list
try:
    import backend.api_cwr  # noqa: F401
    import backend.api_seawide  # noqa: F401
except ImportError:
    # if modules missing an ImportError will be logged but server still runs
    pass

if __name__ == '__main__':
    app.run()
