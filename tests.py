import pytest

from parser import action, range_regex, expand_relevant_data, build_output


# Monday through wednesday is square, thurs/fri is double
@pytest.mark.parametrize("day, value, expected_action, expected_value", [
    ("mon", 4, "square", 16),
    ("tue", 3, "square", 9),
    ("wed", 50, "square", 2500),
    ("thu", 50, "double", 100),
    ("fri", 3, "double", 6),

])
def test_square_vs_double(day, value, expected_action, expected_value):
    result = action(day=day, value=value)
    assert result.get(expected_action) == expected_value


# Test the range regex, i am aware there is a bug if you put fri-mon
@pytest.mark.parametrize("string, result", [
    ("mon", False),
    ("mon-thu", True),
    ("xyz", False),
    ("xyz-thu", False),
    ("fri-zxy", False),
    ("tue-fri", True),
])
def test_range_regex(string, result):
    assert bool(range_regex.match(string)) == result


# Test ranges are expanded
def test_expand_range():
    data = {'mon': 1,
            'tue-thu': 2,
            'fri': 3}
    expected_output = {'mon': 1,
                       'tue': 2,
                       'wed': 2,
                       'thu': 2,
                       'fri': 3}

    assert expand_relevant_data(data) == expected_output


@pytest.mark.parametrize("day_values, desc_prefix, output", [
    ({'mon': '3', 'tue': '3', 'wed': '2', 'thu': '2', "fri": '1'}, "third_desc",
     [{'day': 'mon', 'description': 'third_desc 9', 'square': 9, 'value': 3},
      {'day': 'tue', 'description': 'third_desc 9', 'square': 9, 'value': 3},
      {'day': 'wed', 'description': 'third_desc 4', 'square': 4, 'value': 2},
      {'day': 'thu', 'description': 'third_desc 4', 'double': 4, 'value': 2},
      {'day': 'fri', 'description': 'third_desc 2', 'double': 2, 'value': 1}])
])
def test_output(day_values, desc_prefix, output):
    assert build_output(day_values=day_values, description_prefix=desc_prefix) == output


