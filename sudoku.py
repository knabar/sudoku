"""
Sudoku puzzle solver
"""

import re

class SudokuException(Exception):
    """ Exception raised when puzzle is not solvable"""
    pass

class Sudoku(dict):
    """ Sudoku puzzle solver """

    def __init__(self, puzzle):
        """ Initialize with string or other Sudoku instance """
        super(Sudoku, self).__init__()
        if isinstance(puzzle, Sudoku):
            for cell, options in puzzle.iteritems():
                self[cell] = options
        else:
            puzzle = re.sub(r'[^0-9\.]', '', puzzle)
            if len(puzzle) != 81:
                raise ValueError("Argument must contain 9*9 digits")
            iterpuzzle = iter(puzzle)
            for row in 'ABCDEFGHI':
                for col in '123456789':
                    val = iterpuzzle.next()
                    if val in '0.':
                        val = '123456789'
                    self[row + col] = val

    def copy(self):
        """ Duplicate puzzle """
        return Sudoku(self)

    def display(self):
        """ Display puzzle """
        maxlen =  max(len(val) if val != '123456789' else 1
                      for val in self.itervalues())
        for row in 'ABCDEFGHI':
            for col in '123456789':
                val = self[row + col]
                if val == '123456789':
                    val = '*'
                print ('%%%ds' % maxlen) % val,
                if col in '36':
                    print '|',
            print
            if row in 'CF':
                print '-' * ((maxlen + 1) * 9 + 3)

    def complexity(self):
        """ Measure how close to being solved the puzzle is """
        return len(''.join(self.itervalues()))

    def solved(self):
        """ Check if puzzle is solved """
        return self.complexity() == 81

    def __process_area(self, rows, cols, func):
        """ Perform given function on a given set of cells """
        area = dict()
        for row in rows:
            for col in cols:
                area[row + col] = self[row + col]
        func(area)

    def __process_areas(self, func):
        """ Perform given function on all rows, columns, and 3x3 blocks """
        for row in 'ABCDEFGHI':
            self.__process_area(row, '123456789', func)
        for col in '123456789':
            self.__process_area('ABCDEFGHI', col, func)
        for rows in ('ABC', 'DEF', 'GHI'):
            for cols in ('123', '456', '789'):
                self.__process_area(rows, cols, func)

    def simplify(self):
        """ Simplify the puzzle by removing impossible options from cells """
        def simplify_area(area):
            """ Simplify an area of the puzzle """
            options = dict()
            for val in area.itervalues():
                options[val] = options.setdefault(val, 0) + 1
            for option, freq in options.iteritems():
                optlen = len(option)
                if optlen == freq: # remove these options from all others
                    for loc in area.keys():
                        selfloc = self[loc]
                        if selfloc != option:
                            for opt in option:
                                if opt in selfloc:
                                    selfloc = selfloc.replace(opt, '')
                            self[loc] = selfloc
                elif optlen < freq:
                    raise SudokuException("Puzzle is not solvable")
        after, before = self.complexity(), 0
        while before != after:
            self.__process_areas(simplify_area)
            after, before = self.complexity(), after
        return self.solved()

    def solve(self):
        """ Simplify and trial-and-error """
        if not self.simplify():
            for i in range(2, 10): # starting with cells that have few options
                cell, options = None, ()
                for cell, options in self.iteritems():
                    if len(options) == i:
                        break
                for option in options:
                    trial = self.copy()  # make a copy of the puzzle
                    trial[cell] = option # and assume a value
                    try:
                        if trial.solve(): # it worked, copy values back to self
                            for cell, options in trial.iteritems():
                                self[cell] = options
                            return True
                    except SudokuException: # did not work, remove and simplify
                        self[cell] = self[cell].replace(option, '')
                        if self.simplify():
                            return True
        return self.solved()

def sample():
    """ Solve a sample puzzle that is considered hard """
    sudoku = Sudoku("""
        8.. ... ...
        ..3 6.. ...
        .7. .9. 2..

        .5. ..7 ...
        ... .45 7..
        ... 1.. .3.

        ..1 ... .68
        ..8 5.. .1.
        .9. ... 4..
    """)
    sudoku.display()
    print
    sudoku.solve()
    sudoku.display()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '-p':
        import cProfile
        cProfile.run("sample()")
    else:
        sample()
