#!/usr/bin/python3
#-*- encoding: Utf-8 -*-
from typing import List, Dict, Set, Tuple, Optional, Union, Any, Sequence
from dataclasses import dataclass
from math import ceil

RAW_TABLE_MODEL_NAME_TO_OBJ = {}

def register_table_model(orig_class : 'TableModel'):

    RAW_TABLE_MODEL_NAME_TO_OBJ[orig_class.RAW_NAME] = orig_class

    return orig_class

def format_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB']:
        if size < 1024.0 or unit == 'MiB':
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024.0

@dataclass
class RawFetchResult:

    result_count : int # Including filtered/other page entries
    pages : int # 1-indexed
    current_page : int # 1-indexed
    displayed_rows : List[Dict[str, Any]] # [{'id': 49, 'cells': ['a', 'b', 'c']}, ...]

@dataclass
class ColumnModel:

    readable_name : str
    raw_name : str

class TableModel:

    has_search_bar : bool = True

    has_pagination : bool = True
    pagination_thresold : Optional[int] = 350

    columns : List[ColumnModel]
    has_visible_headers : bool = True

    has_selectable_rows : bool = True

    def query_rows(self,
            server_connection : 'ServerConnection' = None, # From "server.py", allows to reference
                # the "search_index" (index_files.Indexer) and "reader" (hbc_file_parser.HBCReader)
                # attributes
            current_row_idx : Optional[int] = None, # Current row if selected,
                # 0-based (within the full table)
            current_page_if_not_current_row : Optional[int] = None, # Current page
                # if otherwise selected, 1-based (from the search results if searching)
            search_query : Optional[str] = None # Text search query, if any
            ) -> RawFetchResult:
            
        raise NotImplementedError('Please subclass me')
    
    def get_json_response(self,
            server_connection : 'ServerConnection' = None, # From "server.py", allows to reference
                # the "search_index" (index_files.Indexer) and "reader" (hbc_file_parser.HBCReader)
                # attributes
            current_row_idx : Optional[int] = None, # Current row if selected,
                # 0-based (within the full table)
            current_page_if_not_current_row : Optional[int] = None, # Current page
                # if otherwise selected, 1-based (from the search results if searching)
            search_query : Optional[str] = None # Text search query, if any
            ) -> dict:
        raw_result : RawFetchResult = self.query_rows(
            server_connection,
            current_row_idx,
            current_page_if_not_current_row,
            search_query
        )
        result = {
            'table': self.RAW_NAME,
            'result_count': raw_result.result_count,
            'pages': raw_result.pages,
            'current_page': raw_result.current_page,
            'model': {
                'has_search_bar': self.has_search_bar,
                'has_pagination': self.has_pagination,
                'pagination_thresold': self.pagination_thresold,
                'columns': [column.readable_name for column in self.columns],
                'has_visible_headers': self.has_visible_headers,
                'has_selectable_rows': self.has_selectable_rows
            },
            'displayed_rows': raw_result.displayed_rows
        }
        return result

@register_table_model
class FunctionsList(TableModel):
    RAW_NAME = 'functions_list'

    def query_rows(self,
            server_connection : 'ServerConnection',
            current_row_idx : Optional[int] = None,
            current_page_if_not_current_row : Optional[int] = None,
            search_query : Optional[str] = None
            ) -> RawFetchResult:
        
        function_count = server_connection.reader.header.functionCount

        # Do search query filtering here
        if search_query and search_query.strip():
            matching_function_ids : List[int] = server_connection.search_index.find_functions_from_substring(
                search_query.strip())

        # Handle the absence of search query
        else:

            matching_function_ids = [i for i in range(function_count)]
        
        # Do pagination filtering and counting here

        total_results = len(matching_function_ids)
        if self.has_pagination:
            page_count = max(1, ceil(total_results / self.pagination_thresold))
            current_page = min(page_count, current_page_if_not_current_row or 1)

            displayed_function_ids = matching_function_ids[
                (current_page - 1) * self.pagination_thresold:
                current_page * self.pagination_thresold]

        else:
            page_count = 1
            current_page = 1
            displayed_function_ids = matching_function_ids

        headers = server_connection.reader.function_headers
        strings = server_connection.reader.strings

        displayed_rows : List[Dict[str, Any]] = [{
            'id': function_id,
            'cells': (
                strings[headers[function_id].functionName] or 'fun_%08x' % headers[function_id].offset,
                '%08x' % headers[function_id].offset,
                str(headers[function_id].bytecodeSizeInBytes)
            )
        } for function_id in displayed_function_ids] # [{'id': 49, 'cells': ['a', 'b', 'c']}, ...]

        result = RawFetchResult(
            result_count = total_results,
            pages = page_count,
            current_page = current_page,
            displayed_rows = displayed_rows
        )

        return result

    columns = [
        ColumnModel('Name', 'name'),
        ColumnModel('Offset', 'offset'),
        ColumnModel('Size', 'size')
    ]

@register_table_model
class HeaderInfo(TableModel):
    RAW_NAME = 'header_info'

    has_search_bar = False
    has_pagination = False
    pagination_thresold = None
    has_selectable_rows = False

    def query_rows(self,
            server_connection : 'ServerConnection',
            current_row_idx : Optional[int] = None,
            current_page_if_not_current_row : Optional[int] = None,
            search_query : Optional[str] = None
            ) -> RawFetchResult:
        
        header = server_connection.reader.header

        displayed_rows = [
            {'id': index, 'cells': cells}
            for index, cells in enumerate([
                ('File size', format_size(header.fileLength)),
                ('String count', str(header.stringCount)),
                ('Function count', str(header.functionCount)),
                ('String section size', format_size(header.stringStorageSize))
            ])
        ]

        result = RawFetchResult(
            result_count = len(displayed_rows),
            pages = 1,
            current_page = 1,
            displayed_rows = displayed_rows
        )

        return result

    columns = [
        ColumnModel('Field', 'field'),
        ColumnModel('Value', 'value')
    ]
