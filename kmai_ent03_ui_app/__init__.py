
# Package initialization
version = "1.0.6"

# Add necessary import for app so it can be imported as a module
try:
    from .app import app
except ImportError:
    # We don't want to fail the import if app can't be imported yet
    # This might happen during setup.py execution
    pass
