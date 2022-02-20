# coding: utf-8
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


@dataclass
class MarkingDefinition:
    opencti: OpenCTIApiClient
    properties: str = """
        id
        standard_id
        entity_type
        parent_types
        definition_type
        definition
        x_opencti_order
        x_opencti_color
        created
        modified
        created_at
        updated_at
    """

    def list(self, **kwargs) -> List:
        """
        List Marking-Definition objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Marking-Definition objects
        """
        filters = kwargs.get("filters", None)
        first = kwargs.get("first", 500)
        after = kwargs.get("after", None)
        order_by = kwargs.get("orderBy", None)
        order_mode = kwargs.get("orderMode", None)
        custom_attributes = kwargs.get("customAttributes", None)
        get_all = kwargs.get("getAll", False)
        with_pagination = kwargs.get("withPagination", False)
        if get_all:
            first = 500

        self.opencti.log(
            "info",
            f"Listing Marking-Definitions with filters {json.dumps(filters)}.",
        )
        query = (
            """
            query MarkingDefinitions($filters: [MarkingDefinitionsFiltering], $first: Int, $after: ID, $orderBy: MarkingDefinitionsOrdering, $orderMode: OrderingMode) {
                markingDefinitions(filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            """
            + (custom_attributes if custom_attributes is not None else self.properties)
            + """
                        }
                    }
                    pageInfo {
                        startCursor
                        endCursor
                        hasNextPage
                        hasPreviousPage
                        globalCount
                    }
                }
            }
        """
        )
        result = self.opencti.query(
            query,
            {
                "filters": filters,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self.opencti.process_multiple(
            result["data"]["markingDefinitions"], with_pagination
        )

    def read(self, **kwargs):

        """
        Read a Marking-Definition object

        :param id: the id of the Marking-Definition
        :param filters: the filters to apply if no id provided
        :return Marking-Definition object
        """
        id_ = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        if id_ is not None:
            self.opencti.log("info", f"Reading Marking-Definition {{{id_}}}.")
            query = (
                """
                query MarkingDefinition($id: String!) {
                    markingDefinition(id: $id) {
                        """
                + self.properties
                + """
                    }
                }
            """
            )
            result = self.opencti.query(query, {"id": id_})
            return self.opencti.process_multiple_fields(
                result["data"]["markingDefinition"]
            )
        if filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            return None
        self.opencti.log(
            "error",
            "[opencti_marking_definition] Missing parameters: id or filters",
        )
        return None

    def create(self, **kwargs):

        """
        Create a Marking-Definition object

        :param definition_type: the definition_type
        :param definition: the definition
        :return Marking-Definition object
        """
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        definition_type = kwargs.get("definition_type", None)
        definition = kwargs.get("definition", None)
        x_opencti_order = kwargs.get("x_opencti_order", 0)
        x_opencti_color = kwargs.get("x_opencti_color", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if definition is not None and definition_type is not None:
            query = (
                """
                mutation MarkingDefinitionAdd($input: MarkingDefinitionAddInput) {
                    markingDefinitionAdd(input: $input) {
                        """
                + self.properties
                + """
                    }
                }
            """
            )
            result = self.opencti.query(
                query,
                {
                    "input": {
                        "definition_type": definition_type,
                        "definition": definition,
                        "x_opencti_order": x_opencti_order,
                        "x_opencti_color": x_opencti_color,
                        "stix_id": stix_id,
                        "created": created,
                        "modified": modified,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["markingDefinitionAdd"]
            )
        self.opencti.log(
            "error",
            "[opencti_marking_definition] Missing parameters: definition and definition_type",
        )
        return None

    def update_field(self, **kwargs):

        """
        Update a Marking definition object field

        :param id: the Marking definition id
        :param input: the input of the field
        :return The updated Marking definition object
        """
        id_ = kwargs.get("id", None)
        input_ = kwargs.get("input", None)
        if id_ is not None and input_ is not None:
            self.opencti.log("info", f"Updating Marking Definition {{{id_}}}")
            query = """
                    mutation MarkingDefinitionEdit($id: ID!, $input: [EditInput]!) {
                        markingDefinitionEdit(id: $id) {
                            fieldPatch(input: $input) {
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
                    "input": input_,
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["markingDefinitionEdit"]["fieldPatch"]
            )
        self.opencti.log(
            "error",
            "[opencti_marking_definition] Missing parameters: id and key and value",
        )
        return None

    def import_from_stix2(self, **kwargs):

        """
        Import an Marking Definition object from a STIX2 object

        :param stixObject: the MarkingDefinition
        :return MarkingDefinition object
        """
        stix_object = kwargs.get("stixObject", None)
        if stix_object is not None:
            definition_type = stix_object["definition_type"]
            definition = stix_object["definition"][stix_object["definition_type"]]
            if stix_object["definition_type"] == "tlp":
                definition_type = definition_type.upper()
                definition = (
                    f"{definition_type}:{stix_object['definition']['tlp'].upper()}"
                )

            # TODO: REMOVE compatibility with OpenCTI 3.X
            if "x_opencti_order" not in stix_object:
                stix_object["x_opencti_order"] = (
                    stix_object["x_opencti_level"]
                    if "x_opencti_level" in stix_object
                    else 0
                )

            return self.opencti.marking_definition.create(
                stix_id=stix_object["id"],
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                definition_type=definition_type,
                definition=definition,
                x_opencti_order=stix_object["x_opencti_order"]
                if "x_opencti_order" in stix_object
                else 0,
                x_opencti_color=stix_object["x_opencti_color"]
                if "x_opencti_color" in stix_object
                else None,
                x_opencti_stix_ids=stix_object["x_opencti_stix_ids"]
                if "x_opencti_stix_ids" in stix_object
                else None,
            )
        self.opencti.log(
            "error", "[opencti_marking_definition] Missing parameters: stixObject"
        )
        return None

    def delete(self, **kwargs):
        id_ = kwargs.get("id", None)
        if id_ is not None:
            self.opencti.log("info", f"Deleting Marking-Definition {{{id_}}}.")
            query = """
                 mutation MarkingDefinitionEdit($id: ID!) {
                     markingDefinitionEdit(id: $id) {
                         delete
                     }
                 }
             """
            self.opencti.query(query, {"id": id_})
        self.opencti.log("error", "[opencti_marking_definition] Missing parameters: id")
