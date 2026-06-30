class InvalidDataCollector:

    def __init__(self):
        self.rows = []

    def add(
        self,
        source,
        file_name,
        row_number,
        reason,
        raw_data
    ):
        self.rows.append([
            source,
            file_name,
            row_number,
            reason,
            str(raw_data)
        ])

    def get_rows(self):
        return self.rows

    def count(self):
        return len(self.rows)

    def clear(self):
        self.rows.clear()