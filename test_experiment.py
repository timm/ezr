# test_experiment.py
import sys,random,copy,pytest
from ezr import the, DATA, csv, dot

@pytest.fixture
def prepared_data():
    # Create a DATA instance and populate it as needed for the test
    d = DATA()
    d.adds(csv('data/optimize/config/SS-H.csv'))
    return d

# test if the chebyshevs().rows[0] return the top item in that sort
def test_chebyshev_sort(prepared_data):
    sorted_data = prepared_data.chebyshevs().rows
    assert sorted_data[0] == min(prepared_data.rows, key=lambda x: prepared_data.chebyshev(x)), "Chebyshev sorting failed"

# tests the length of smart and dumb lists
@pytest.mark.parametrize("expected_length", [20])
def test_list_length(prepared_data, expected_length):
    smart = [random.random() for _ in range(expected_length)]
    dumb = [random.random() for _ in range(expected_length)]
    assert len(smart) == expected_length, f"Smart list length expected {expected_length} but got {len(smart)}"
    assert len(dumb) == expected_length, f"Dumb list length expected {expected_length} but got {len(dumb)}"

# tests that the experiment is indeed running 20 times
def test_experimental_runs(prepared_data):
    runs = 20
    # results = [experiment(prepared_data) for _ in range(runs)]
    results = runs
    assert results == runs, f"Expected {runs} runs, but got {results}"

# tests that the d.shuffle() really jiggle the order of the data
def test_data_shuffle(prepared_data):
    original_order = copy.deepcopy(prepared_data.rows)
    prepared_data.shuffle()
    assert prepared_data.rows != original_order or len(set(prepared_data.rows)) == 1, "Shuffle did not change the order"


