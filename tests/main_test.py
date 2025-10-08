from main import find_all_taxis


def test_find_all_taxis():
  taxis = find_all_taxis()
  assert taxis.count() > 5
