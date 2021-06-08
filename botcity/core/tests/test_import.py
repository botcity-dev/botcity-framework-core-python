def test_package_import():
    import botcity.core as core
    assert core.__file__ != ""
