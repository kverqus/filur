from .pattern import Pattern

import os
import re


class File:
    def __init__(self, path: str, direction: str, order_by: str, rows: int, output_type: str, output_path: str, patterns: list):
        self.path = path
        self.direction = direction
        self.order_by = order_by
        self.rows = rows
        self.output_type = output_type
        self.output_path = output_path
        self.patterns = patterns

    def _reverse_readline(self, path: str, buf_size: int = 8192):
        """A generator that returns the lines of a file in reverse order"""
        with open(path, 'rb') as fh:
            segment = None
            offset = 0
            fh.seek(0, os.SEEK_END)
            file_size = remaining_size = fh.tell()

            while remaining_size > 0:
                offset = min(file_size, offset + buf_size)
                fh.seek(file_size - offset)
                buffer = fh.read(min(remaining_size, buf_size))

                # remove file's last "\n" if it exists, only for the first buffer
                if remaining_size == file_size and buffer[-1] == ord('\n'):
                    buffer = buffer[:-1]

                remaining_size -= buf_size
                lines = buffer.split('\n'.encode())

                # append last chunk's segment to this chunk's last line
                if segment is not None:
                    lines[-1] += segment

                segment = lines[0]
                lines = lines[1:]

                # yield lines in this chunk except the segment
                for line in reversed(lines):
                    # only decode on a parsed line, to avoid utf-8 decode error
                    yield line.decode()

            # Don't yield None if the file was empty
            if segment is not None:
                yield segment.decode()

    def _read_file(self) -> list:
        data = []

        if self.direction == 'reverse':
            data = self._reverse_readline(self.path)

        else:
            with open(self.path, 'r', encoding='utf-8') as file:
                data = file.readlines()

        return data

    def _matches(self, patterns: list, row: str) -> dict:
        result = {
            'patterns': [],
            'matches': []
        }

        for pattern in patterns:
            if self._matches_pattern(row, pattern):
                result['patterns'].append(pattern)
                result['matches'].append(True)
            else:
                result['matches'].append(False)

        return result

    def _match_row(self, row: str) -> dict:
        result = {}
        matched_patterns = []
        and_conditions = [
            pattern for pattern in self.patterns if pattern.operator.upper() == 'AND']
        or_conditions = [
            pattern for pattern in self.patterns if pattern.operator.upper() == 'OR']
        not_conditions = [
            pattern for pattern in self.patterns if pattern.operator.upper() == 'NOT']
        keyword_conditions = [
            pattern for pattern in self.patterns if pattern.operator.upper() == 'KEYWORD']
        and_matches = self._matches(and_conditions, row)
        or_matches = self._matches(or_conditions, row)
        not_matches = self._matches(not_conditions, row)
        keyword_matches = self._matches(keyword_conditions, row) if and_conditions or or_conditions else {}
        and_match = all(and_matches['matches'])
        or_match = any(or_matches['matches'])
        not_match = all(not_matches['matches'])

        for match in [and_matches, or_matches, not_matches, keyword_matches]:
            for pattern in match['patterns']:
                matched_patterns.append(pattern.to_dict())

        if (not and_conditions or and_match) and (not or_conditions or or_match) and (not not_conditions or not not_match):
            result['patterns'] = matched_patterns
            result['combined_weight'] = sum(
                [pattern['weight'] for pattern in matched_patterns])
            result['row'] = row

        return result

    def _matches_pattern(self, row: str, pattern) -> bool:
        match pattern.type:
            case 'regex':
                return re.search(pattern.pattern, row) is not None
            case 'string':
                return pattern.pattern in row
            case _:
                return False

    def _match_rows(self, data: list) -> dict:
        result = {
            'matched_rows': 0,
            'rows': []
        }

        for idx, row in enumerate(data):
            if not self.rows == -1 and idx >= self.rows:
                break

            row = self._match_row(row)

            if row:
                result['rows'].append(row)
                result['matched_rows'] += 1

        if self.order_by == 'weight':
            result['rows'] = sorted(
                result['rows'], key=lambda d: d['combined_weight'], reverse=True)

        return result

    def process(self):
        if not os.path.exists(self.path):
            raise OSError(f"{self.path} not found")

        data = self._read_file()
        result = self._match_rows(data)

        return result

    @classmethod
    def from_dict(cls, data: dict):
        # Set defaults in case nothing is specified in the playbook
        direction = data.get('direction', 'forward')
        order_by = data.get('order_by', 'none')
        rows = data.get('rows', -1)
        output = data.get('output', {})
        output_type = output.get('type', 'console')
        output_path = output.get('path', '')

        # Create Pattern objects from each pattern
        patterns = [Pattern(**pattern_data)
                    for pattern_data in data.get('patterns', [])]

        # Instantiate and return a File object with the Pattern objects
        return cls(
            path=data['file'],
            direction=direction,
            order_by=order_by,
            rows=rows,
            output_type=output_type,
            output_path=output_path,
            patterns=patterns
        )

    def __repr__(self):
        return f"File(path={self.path}, direction={self.direction}, order_by={self.order_by}, rows={self.rows}, output_type={self.output_type}, output_path={self.output_path}, patterns={self.patterns})"
