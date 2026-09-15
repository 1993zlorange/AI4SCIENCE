def test_package_can_be_imported() -> None:
    import ai_project

    assert ai_project.__name__ == "ai_project"
