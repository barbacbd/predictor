from predictor.config import process_clusters, Config
from predictor.log import get_logger
from predictor.file import create_output_file, read_data, highlight_selections
from predictor.clusters.selection import select
from logging import getLogger
from os.path import abspath, join, dirname
import pytest
import pandas as pd
from os import remove
from openpyxl import load_workbook


def test_process_clusters_valid():
    '''Test good cluster values'''
    min_cluster, max_cluster = process_clusters([1, 100])
    assert min_cluster == 1
    assert max_cluster == 100


def test_process_clusters_invalid_type():
    '''Test invalid type passed to the function. Not a 
    list of tuple'''
    with pytest.raises(AttributeError):
        min_cluster, max_cluster = process_clusters(100)
    

def test_process_clusters_empty():
    '''The list or tuple must be of a length >= 1'''
    with pytest.raises(AttributeError):
        min_cluster, max_cluster = process_clusters([])    


def test_process_clusters_single_item_list():
    '''The same result is returned for min and max clusters 
    when a single item list is used'''
    min_cluster, max_cluster = process_clusters([100])
    assert min_cluster == 100
    assert max_cluster == 100


def test_process_cluster_too_small():
    '''Test clusters too small min'''
    with pytest.raises(AttributeError):
        min_cluster, max_cluster = process_clusters([0, 100])


def test_process_clusters_valid_out_of_order():
    '''Test good cluster values, but the values are out of order'''
    min_cluster, max_cluster = process_clusters([100, 1])
    assert min_cluster == 1
    assert max_cluster == 100
    
    
def test_process_cluster_too_small_out_of_order():
    '''Test clusters too small min, but out of order'''
    with pytest.raises(AttributeError):
        min_cluster, max_cluster = process_clusters([100, 0])


def test_logging_creation():
    '''Test the creation of the logger. Check the number of handlers'''
    log = get_logger()
    assert len(log.handlers) == 1


def test_create_output_file():
    '''Create the filename for the output file given the input name'''
    filename = join(dirname(abspath(__file__)), "test_files/AMO_Index.txt")
    assert create_output_file(filename) == "AMO_Index_analysis.xlsx"


def test_create_read_file_success():
    '''Test reading in the text file success'''
    filename = join(dirname(abspath(__file__)), "test_files/AMO_Index.txt")
    assert read_data(filename) is not None


def test_create_read_file_failure():
    '''Test reading in the text file failure'''
    filename = join(dirname(abspath(__file__)), "test_files/DoesNotExist.txt")
    with pytest.raises(FileNotFoundError):
        read_data(filename) is None
    

def test_highlighting_selections():
    '''Create fake data and add it to the xlsx spreadsheet. Then
    highlight the correct selections. Close the file, reopen the file
    and check that the selections are highlighted.
    '''
    max = 20
    length = max - 2 + 1

    vals = [x for x in range(int(length/2))]
    vals.extend(vals[::-1])

    cols = [str(x) for x in range(2, max+1)]
    if len(vals) < len(cols):
        vals.append(vals[len(vals)-1])

    df = pd.DataFrame(data={'Dunn': vals}, index=cols)
    df = df.T
    selections = select(df)

    with pd.ExcelWriter("test.xlsx", engine='xlsxwriter') as w:
        df.style.apply(highlight_selections, selections=selections, axis=None).to_excel(w, sheet_name="test")

    wb = load_workbook("test.xlsx", data_only=True)
    sheet = wb['test']
    
    colors_in_hex = set()
    
    # Always Row 2, column will differ
    for i in range(length+1):
        colors_in_hex.add(sheet[f'{chr(i+65)}2'].fill.start_color.index)
    
    remove("test.xlsx")
    assert len(colors_in_hex) == 2


def test_create_config_from_file_valid():
    '''Create a configuration from a valid file'''


def test_create_config_invalid_data():
    '''Create a configuration from invalid file data. Certain values 
    will be missing while some are valid/present in the file data.'''
    


def test_create_config_invalid_filename():
    '''file does not, exist. Configuration creation failure.'''


