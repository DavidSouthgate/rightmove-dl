class CsvWriter:
    file = None

    def __init__(self, filename):
        self.file = open(filename, "w")

    def write(self, *columns):
        if self.file is None: return
        for i in range(0, len(columns)):
            column = columns[i]
            self._write_value(column)
            if i < len(columns) - 1:
                self.file.write(",")
        self.file.write("\n")

    def _write_value(self, value):
        if value is None:
            return
        if isinstance(value, int) or isinstance(value, float):
            self.file.write(str(value))
        else:
            self.file.write("\"" + str(value).replace("\"", "\\\"") + "\"")

    def close(self):
        if self.file is None: return
        self.file.close()