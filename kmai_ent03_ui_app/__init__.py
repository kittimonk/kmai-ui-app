
# Package initialization
version = "1.0.6"

# Add necessary import for app so it can be imported as a module
try:
    from .app import app
except ImportError:
    # We don't want to fail the import if app can't be imported yet
    # This might happen during setup.py execution
    import sys
    import os
    # Try adding the current directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from .app import app
    except ImportError:
        # We still don't want to fail the import if app can't be imported
        pass
