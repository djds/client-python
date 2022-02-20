# coding: utf-8
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


@dataclass
class Label:
    opencti: OpenCTIApiClient
    properties: str = """
        id
        value
        color
        created_at
        updated_at
        standard_id
    """

    def list(self, **kwargs):
        """
        List Label objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Label objects
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

        self.opencti.log("info", f"Listing Labels with filters {json.dumps(filters)}.")
        query = (
            """
            query Labels($filters: [LabelsFiltering], $first: Int, $after: ID, $orderBy: LabelsOrdering, $orderMode: OrderingMode) {
                labels(filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
        return self.opencti.process_multiple(result["data"]["labels"], with_pagination)

    def read(self, **kwargs):
        """
        Read a Label object

        :param id: the id of the Label
        :param filters: the filters to apply if no id provided
        :return Label object
        """

        id_ = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        if id_ is not None:
            self.opencti.log("info", f"Reading label {{{id_}}}.")
            query = (
                """
                query Label($id: String!) {
                    label(id: $id) {
                        """
                + self.properties
                + """
                    }
                }
            """
            )
            result = self.opencti.query(query, {"id": id_})
            return self.opencti.process_multiple_fields(result["data"]["label"])
        if filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            return None
        self.opencti.log("error", "[opencti_label] Missing parameters: id or filters")
        return None

    def create(self, **kwargs):
        """
        Create a Label object

        :param value: the value
        :param color: the color
        :return label object
        """
        stix_id = kwargs.get("stix_id", None)
        value = kwargs.get("value", None)
        color = kwargs.get("color", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)

        if value is not None:
            query = (
                """
                mutation LabelAdd($input: LabelAddInput) {
                    labelAdd(input: $input) {
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
                        "stix_id": stix_id,
                        "value": value,
                        "color": color,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["labelAdd"])
        self.opencti.log(
            "error",
            "[opencti_label] Missing parameters: value",
        )
        return None

    def update_field(self, **kwargs):
        """
        Update a Label object field

        :param id: the Label id
        :param input: the input of the field
        :return The updated Label object
        """
        id_ = kwargs.get("id", None)
        input_ = kwargs.get("input", None)
        if id_ is not None and input_ is not None:
            self.opencti.log("info", f"Updating Label {{{id_}}}.")
            query = """
                    mutation LabelEdit($id: ID!, $input: [EditInput]!) {
                        labelEdit(id: $id) {
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
                result["data"]["labelEdit"]["fieldPatch"]
            )
        self.opencti.log(
            "error",
            "[opencti_label] Missing parameters: id and key and value",
        )
        return None

    def delete(self, **kwargs):
        id_ = kwargs.get("id", None)
        if id_ is not None:
            self.opencti.log("info", f"Deleting Label {{{id_}}}.")
            query = """
                 mutation LabelEdit($id: ID!) {
                     labelEdit(id: $id) {
                         delete
                     }
                 }
             """
            self.opencti.query(query, {"id": id_})
        self.opencti.log("error", "[opencti_label] Missing parameters: id")
