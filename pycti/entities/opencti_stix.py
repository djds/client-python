# coding: utf-8

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


@dataclass
class Stix:
    opencti: OpenCTIApiClient

    def delete(self, **kwargs) -> None:
        """
        Delete a Stix element

        :param id_: the Stix element id
        :return void
        """
        id_ = kwargs.get("id", None)
        if id_ is not None:
            self.opencti.log("info", f"Deleting Stix element {{{id_}}}.")
            query = """
                 mutation StixEdit($id: ID!) {
                     stixEdit(id: $id) {
                         delete
                     }
                 }
             """
            self.opencti.query(query, {"id": id_})
        else:
            self.opencti.log("error", "[opencti_stix] Missing parameters: id")
