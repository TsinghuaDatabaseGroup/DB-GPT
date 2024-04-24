from functools import total_ordering


@total_ordering
class Index:
    def __init__(self, columns, estimated_size=None):
        if len(columns) == 0:
            raise ValueError("Index needs at least 1 column")
        self.columns = tuple(columns)
        # Store hypopg estimated size when `store_size=True` (whatif)
        self.estimated_size = estimated_size
        self.hypopg_name = None

    # Used to sort indexes
    def __lt__(self, other):
        if len(self.columns) != len(other.columns):
            return len(self.columns) < len(other.columns)

        return self.columns < other.columns

    def __repr__(self):
        columns_string = ",".join(map(str, self.columns))
        # return f"I({columns_string})"
        return f"{columns_string}"

    def __eq__(self, other):
        if not isinstance(other, Index):
            return False

        return self.columns == other.columns

    def __hash__(self):
        return hash(self.columns)

    def _column_names(self):
        return [x.name for x in self.columns]

    def is_single_column(self):
        return True if len(self.columns) == 1 else False

    def table(self):
        assert (
            self.columns[0].table is not None
        ), "Table should not be None to avoid false positive comparisons."
        return self.columns[0].table

    def index_idx(self):
        columns = "_".join(self._column_names())
        return f"{self.table()}_{columns}_idx"

    def joined_column_names(self):
        return ",".join(self._column_names())

    def appendable_by(self, other):
        if not isinstance(other, Index):
            return False

        if self.table() != other.table():
            return False

        if not other.is_single_column():
            return False

        if other.columns[0] in self.columns:
            return False

        return True

    def subsumes(self, other):
        if not isinstance(other, Index):
            return False
        return self.columns[:len(other.columns)] == other.columns

    def prefixes(self):
        """
        Consider I(K;S). For any prefix K' of K (including K' = K if S is not
        empty), an index I_P = (K';Ø) is obtained.
        Returns a list of index prefixes ordered by decreasing width.
        """
        index_prefixes = []
        for prefix_width in range(len(self.columns) - 1, 0, -1):
            index_prefixes.append(Index(self.columns[:prefix_width]))
        return index_prefixes


# The following methods implement the index transformation rules presented by
# Bruno and Chaudhuri their 2005 paper Automatic Physical Database Tuning:
# A Relaxation-based Approach.
#   The "removal" transformation is not implemented, because it does not directly work on
#     index objects, but more on an index configuration.
#   The "promotion to clustered" transformation is not implemented, because clustered
#     indexes are currently not chosen by selection algorithms
#   The "prefixing" is implemented as method of the Index class
#
# The authors define an index I as a sequence of key columns K and a set of suffix
# columns S: I = (K;S). If the database system does not support suffix columns, only
# key columns are considered.

# A merged index is the best index that can answer all requests that either previous
# index did. Merging I_1(K_1;S_1) and I_2(K_2;S_2) results in
# I_1_2 = (K1;(S_1 ∪ K_2 ∪ S_2) - K_1).
# If K_1 is a prefix of K_2, I_1_2 = (K2; (S_1 ∪ S_2) - K_2)).
# Returns the merged index.
def index_merge(index_1, index_2):
    assert index_1.table() == index_2.table()
    merged_columns = list(index_1.columns)
    for column in index_2.columns:
        if column not in index_1.columns:
            merged_columns.append(column)
    return Index(merged_columns)


# Splitting two indexes produces a common index I_C and at most two additional
# residual indexes I_R1 and I_R2. Splitting I_1(K_1;S_1) and I_2(K_2;S_2):
# I_C = (K_C;S_C) with K_C = K_1 ∩ K_2 and S_C = S_1 ∩ S_2 where K_C cannot be empty.
# Split is undefined if K_1 and K_2 have no common columns. If K_1 and K_C are different:
# I_R_1 = (K_1 - K_C, I_1 - I_C) and if K_2 and K_C are different
# I_R_2 = (K_2 - K_C, I_2 - I_C).
# Returns None if K_1 and K_2 have no common columns or a set: {I_C, I_R_1, I_R_2} where
# both I_R_1 are I_R_2 optional.
def index_split(index_1, index_2):
    assert index_1.table() == index_2.table()
    common_columns = []
    index_1_residual_columns = []
    for column in index_1.columns:
        if column in index_2.columns:
            common_columns.append(column)
        else:
            index_1_residual_columns.append(column)
    if len(common_columns) == 0:
        return None
    result = {Index(common_columns)}

    if len(index_1_residual_columns) > 0:
        result.add(Index(index_1_residual_columns))

    index_2_residual_columns = []
    for column in index_2.columns:
        if column not in index_1.columns:
            index_2_residual_columns.append(column)
    if len(index_2_residual_columns) > 0:
        result.add(Index(index_2_residual_columns))

    return result
