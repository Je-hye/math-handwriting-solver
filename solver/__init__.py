def run(*args, **kwargs):
    from .pipeline import run as _run
    return _run(*args, **kwargs)

__all__ = ["run"]
