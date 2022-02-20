# coding: utf-8
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.opencti_api_client import File, OpenCTIApiClient


@dataclass
class StixCoreObject:
    opencti: OpenCTIApiClient
    file: File

    def merge(self, **kwargs):
        """
        Update a Stix-Domain-Object object field

        :param id: the Stix-Domain-Object id
        :param key: the key of the field
        :param value: the value of the field
        :return The updated Stix-Domain-Object object
        """
        id_ = kwargs.get("id", None)
        stix_core_objects_ids = kwargs.get("object_ids", None)
        if id_ is not None and stix_core_objects_ids is not None:
            self.opencti.log(
                "info",
                f"Merging Core object {{{id_}}} with {{{','.join(stix_core_objects_ids)}}}.",
            )
            query = """
                    mutation StixCoreObjectEdit($id: ID!, $stixCoreObjectsIds: [String]!) {
                        stixCoreObjectEdit(id: $id) {
                            merge(stixCoreObjectsIds: $stixCoreObjectsIds) {
                                id
                                standard_id
                                entity_type
                            }
                        }
                    }
                """
            result = self.opencti.query(
                query,
                {
                    "id": id_,
                    "stixCoreObjectsIds": stix_core_objects_ids,
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["stixCoreObjectEdit"]["merge"]
            )
        self.opencti.log(
            "error",
            "[opencti_stix_core_object] Missing parameters: id and object_ids",
        )
        return None

    def list_files(self, **kwargs):
        id_ = kwargs.get("id", None)
        self.opencti.log(
            "info",
            f"Listing files of Stix-Core-Object {{ {id_} }}",
        )
        query = """
                    query StixCoreObject($id: String!) {
                        stixCoreObject(id: $id) {
                            importFiles {
                                edges {
                                    node {
                                        id
                                        name
                                        size
                                        metaData {
                                            mimetype
                                            version
                                        }
                                    }
                                }
                            }
                        }
                    }
                """
        result = self.opencti.query(query, {"id": id_})
        entity = self.opencti.process_multiple_fields(result["data"]["stixCoreObject"])
        return entity["importFiles"]
