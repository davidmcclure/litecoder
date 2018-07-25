

from sqlalchemy import Column, Integer, ForeignKey, func

from tqdm import tqdm
from collections import defaultdict
from scipy.spatial import cKDTree

from .base import BaseModel
from .wof_locality import WOFLocality
from .. import logger
from ..db import session


ID_COLS = (
    'dbp_id',
    'fb_id',
    'fct_id',
    'fips_code',
    'gn_id',
    'gp_id',
    'loc_id',
    'nyt_id',
    'qs_id',
    'qs_pg_id',
    'wd_id',
    'wk_page',
)


class WOFLocalityDup(BaseModel):

    __tablename__ = 'wof_locality_dup'

    id = Column(Integer, primary_key=True)

    wof_id = Column(Integer, ForeignKey(WOFLocality.wof_id))

    @classmethod
    def update(cls, wof_ids):
        """Merge in new dupes.
        """
        session.bulk_save_objects([cls(wof_id=wof_id) for wof_id in wof_ids])
        session.commit()

    @classmethod
    def dedupe_id_col(cls, col_name):
        """Dedupe localities via shared external identifier.
        """
        dup_col = getattr(WOFLocality, col_name)

        logger.info('Mapping `%s` -> rows' % col_name)

        id_rows = defaultdict(list)
        for row in tqdm(WOFLocality.query.filter(dup_col != None)):
            id_rows[getattr(row, col_name)].append(row)

        logger.info('Deduping rows with shared `%s`' % col_name)

        dupes = set()
        for rows in tqdm(id_rows.values()):
            if len(rows) > 1:

                # Sort by completeness.
                rows = sorted(rows, key=lambda r: r.field_count, reverse=True)

                # Add all but most complete to dupes.
                for row in rows[1:]:
                    dupes.add(row.wof_id)

        cls.update(dupes)
        return len(dupes)

    @classmethod
    def dedupe_proximity(cls, buffer=0.1):
        """For each locality, get neighbors within N degrees. If any of these
        (a) has the same name and (b) has more complete metadata, set dupe.
        """
        # Pre-load rows.
        rows = WOFLocality.query.all()
        id_row = {i: row for i, row in enumerate(rows)}

        # Build index.
        data = [[r.longitude, r.latitude] for r in rows]
        idx = cKDTree(data)

        logger.info('Deduping rows within %.2f°' % buffer)

        dupes = set()
        for id1, id2 in tqdm(idx.query_pairs(buffer)):

            row1, row2 = id_row[id1], id_row[id2]

            if row1.name == row2.name:

                dupes.add(
                    row1.wof_id if row1.field_count < row2.field_count
                    else row2.wof_id
                )

        cls.update(dupes)
        return len(dupes)

    @classmethod
    def dedupe(cls):
        """Dedupe on all id cols + proximity.
        """
        cls.query.delete()

        for name in ID_COLS:
            cls.dedupe_id_col(name)

        cls.dedupe_proximity()

    @classmethod
    def count_unique(cls):
        """Count unique duplicate rows.
        """
        return session.query(cls.wof_id.distinct()).count()
