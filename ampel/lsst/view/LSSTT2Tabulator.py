#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : Ampel-LSST/ampel/lsst/view/LSSTT2Tabulator.py
# License           : BSD-3-Clause
# Author            : Marcus Fenner <mf@physik.hu-berlin.de>
# Date              : 25.05.2021
# Last Modified Date: 13.09.2021
# Last Modified By  : Marcus Fenner <mf@physik.hu-berlin.de>

from typing import Any, List, Sequence, Tuple

from ampel.content.DataPoint import DataPoint
from astropy.table import Table

from ampel.abstract.AbsT2Tabulator import AbsT2Tabulator

LSST_BANDPASSES = {
    "u": "lsstu",
    "g": "lsstg",
    "r": "lsstr",
    "i": "lssti",
    "z": "lsstz",
    "y": "lssty",
}


class LSSTT2Tabulator(AbsT2Tabulator):
    convert2jd: bool = True
    """ """

    def get_flux_table(
        self,
        dps: List[DataPoint],
    ) -> Table:
        flux, fluxerr, filtername, tai = self.get_values(
            dps, ["psFlux", "psFluxErr", "filterName", "midPointTai"]
        )
        if self.convert2jd:
            tai = self._to_jd(tai)
        filters = list(map(LSST_BANDPASSES.get, filtername))
        return Table(
            {
                "time": tai,
                "flux": flux,
                "fluxerr": fluxerr,
                "band": filters,
                "zp": [25] * len(filters),
                "zpsys": ["ab"] * len(filters),
            },
            dtype=("float64", "float64", "float64", "str", "int64", "str"),
        )

    def get_pos(self, dps: List[DataPoint]) -> Sequence[Tuple[float, float]]:
        return tuple(zip(*self.get_values(dps, ["ra", "decl"])))

    def get_jd(self, dps: List[DataPoint]) -> Sequence[float]:
        return self._to_jd(self.get_values(dps, "midPointTai")[0])

    @staticmethod
    def _to_jd(dates: Sequence[Any]) -> Sequence[Any]:
        return [date + 2400000.5 for date in dates]

    def get_stock_id(self, dps: List[DataPoint]) -> set[int]:
        return set([el["stock"] for el in dps if "ZTF" in el["tag"]])  # type: ignore[misc]

    def get_stock_name(self, dps: List[DataPoint]) -> set[int]:  # type: ignore[override]
        return self.get_stock_id(dps)

    @staticmethod
    def get_values(
        dps: List[DataPoint], params: Sequence[str]
    ) -> Tuple[Sequence[Any], ...]:
        if tup := tuple(
            map(
                list,
                zip(
                    *(
                        [el["body"][param] for param in params]
                        for el in dps
                        if "LSST" in el["tag"]
                    )
                ),
            )
        ):
            return tup
        else:
            return tuple([[]] * len(params))
