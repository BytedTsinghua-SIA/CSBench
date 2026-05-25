try:
    import importlib.metadata
    __version__ = importlib.metadata.version("cs336-systems")
except Exception:
    __version__ = "1.0.5"