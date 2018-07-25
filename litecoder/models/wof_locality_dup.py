

from sqlalchemy import Column, Integer, ForeignKey, func

from tqdm import tqdm
from scipy.spatial import cKDTree

from .base import BaseModel
from .wof_locality import WOFLocality
from ..db import session


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
    def dedupe_by_proximity(cls, buffer=0.1):
        """For each locality, get neighbors within N degrees. If any of these
        (a) has the same name and (b) has more complete metadata, set dupe.
        """
        # Pre-load rows.
        rows = WOFLocality.query.all()
        id_row = {i: row for i, row in enumerate(rows)}

        # Build index.
        data = [[r.longitude, r.latitude] for r in rows]
        idx = cKDTree(data)

        dupes = set()
        for id1, id2 in tqdm(idx.query_pairs(buffer)):

            row1, row2 = id_row[id1], id_row[id2]

            if row1.name == row2.name:

                dupes.add(
                    row1.wof_id if row1.field_count < row2.field_count
                    else row2.wof_id
                )

        cls.update(dupes)

    @classmethod
    def dedupe_shared_id_col(cls, col_name):
        """Dedupe localities via shared external identifier.
        """
        dup_col = getattr(WOFLocality, col_name)

        # Select ids with 2+ records.
        query = (session
            .query(dup_col)
            .filter(dup_col != None)
            .group_by(dup_col)
            .having(func.count(WOFLocality.wof_id) > 1)
            .all())

        dupes = set()
        for r in tqdm(query):

            # Load rows, sort by completeness.
            rows = WOFLocality.query.filter(dup_col==r[0])
            rows = sorted(rows, key=lambda r: r.field_count, reverse=True)

            # Add all but most complete to dupes.
            for row in rows[1:]:
                dupes.add(row.wof_id)

        cls.update(dupes)
