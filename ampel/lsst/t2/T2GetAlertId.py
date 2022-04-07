#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File:                Ampel-LSST/ampel/lsst/t2/T2GetAlertId.py
# License:             BSD-3-Clause
# Author:              Marcus Fennner <mf@physik.hu-berlinn.de>
# Date:                31.03.2022
# Last Modified Date:  31.03.2022
# Last Modified By:    Marcus Fennner <mf@physik.hu-berlinn.de>

from typing import ClassVar, List, Union, Sequence, Dict, Literal
from ampel.types import UBson
from ampel.abstract.AbsTiedPointT2Unit import AbsTiedPointT2Unit
from ampel.view.T2DocView import T2DocView
from ampel.content.DataPoint import DataPoint
from ampel.struct.UnitResult import UnitResult
from ampel.model.DPSelection import DPSelection
from ampel.model.UnitModel import UnitModel


class T2GetAlertId(AbsTiedPointT2Unit):
    """
    Get first alertId associated with the latest datapoint in a T1
    """

    eligible: ClassVar[DPSelection] = DPSelection(
        filter="LSSTDPFilter", sort="diaSourceId", select="last"
    )
    t2_dependency: Sequence[UnitModel[Literal["T2GetAlertJournal"]]]

    def process(
        self, datapoint: DataPoint, t2_views: Sequence[T2DocView]
    ) -> Union[UBson, UnitResult]:
        sourceid = datapoint["body"]["diaSourceId"]
        t0journals: List[Dict] = []
        for t2_view in t2_views:
            if not t2_view.unit == "T2GetAlertJournal":
                continue
            payload = t2_view.get_payload()
            assert type(payload) is list
            for journal in payload:
                if sourceid in journal["upsert"]:
                    t0journals += [journal]
        if not t0journals:
            return {}
        t0journals.sort(key=lambda x: x["ts"])
        runids = set([t0journal["run"] for t0journal in t0journals])
        if len(runids) > 1:
            self.logger.warn(
                f"Multiple runids found {runids}, assuming latest"
            )
            t0journals = [
                journal
                for journal in t0journals
                if journal["run"] == sorted(runids)[-1]
            ]
        first = t0journals[0]
        return {"ts": first["ts"], "alertId": first["alert"]}
