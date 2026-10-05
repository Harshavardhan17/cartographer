from cartographer import __version__


def test_package_exposes_a_version() -> None:
    assert isinstance(__version__, str)
    assert __version__.count(".") == 2