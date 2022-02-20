# coding: utf-8
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


@dataclass
class KillChainPhase:
    opencti: OpenCTIApiClient
    properties: str = """
        id
        standard_id
        entity_type
        parent_types
        kill_chain_name
        phase_name
        x_opencti_order
        created
        modified
        created_at
        updated_at
    """

    def list(self, **kwargs):
        """
        List Kill-Chain-Phase objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Kill-Chain-Phase objects
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
            "info", f"Listing Kill-Chain-Phase with filters {json.dumps(filters)}."
        )
        query = (
            """
            query KillChainPhases($filters: [KillChainPhasesFiltering], $first: Int, $after: ID, $orderBy: KillChainPhasesOrdering, $orderMode: OrderingMode) {
                killChainPhases(filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            result["data"]["killChainPhases"], with_pagination
        )

    def read(self, **kwargs):
        """
        Read a Kill-Chain-Phase object

        :param id: the id of the Kill-Chain-Phase
        :param filters: the filters to apply if no id provided
        :return Kill-Chain-Phase object
        """
        id_ = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        if id_ is not None:
            self.opencti.log("info", f"Reading Kill-Chain-Phase {{{id_}}}.")
            query = (
                """
                query KillChainPhase($id: String!) {
                    killChainPhase(id: $id) {
                        """
                + self.properties
                + """
                    }
                }
            """
            )
            result = self.opencti.query(query, {"id": id_})
            return self.opencti.process_multiple_fields(
                result["data"]["killChainPhase"]
            )
        if filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            return None
        self.opencti.log(
            "error", "[opencti_kill_chain_phase] Missing parameters: id or filters"
        )
        return None

    def create(self, **kwargs):
        """
        Create a Kill-Chain-Phase object

        :param name: the name of the Kill-Chain-Phase
        :return Kill-Chain-Phase object
        """
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        kill_chain_name = kwargs.get("kill_chain_name", None)
        phase_name = kwargs.get("phase_name", None)
        x_opencti_order = kwargs.get("x_opencti_order", 0)

        if kill_chain_name is not None and phase_name is not None:
            self.opencti.log("info", f"Creating Kill-Chain-Phase {{{phase_name}}}.")
            query = (
                """
                mutation KillChainPhaseAdd($input: KillChainPhaseAddInput) {
                    killChainPhaseAdd(input: $input) {
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
                        "created": created,
                        "modified": modified,
                        "kill_chain_name": kill_chain_name,
                        "phase_name": phase_name,
                        "x_opencti_order": x_opencti_order,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["killChainPhaseAdd"]
            )
        self.opencti.log(
            "error",
            "[opencti_kill_chain_phase] Missing parameters: kill_chain_name and phase_name",
        )
        return None

    def update_field(self, **kwargs):
        """
        Update a Kill chain object field

        :param id: the Kill chain id
        :param input: the input of the field
        :return The updated Kill chain object
        """
        id_ = kwargs.get("id", None)
        input_ = kwargs.get("input", None)
        if id_ is not None and input_ is not None:
            self.opencti.log("info", f"Updating Kill chain {{{id_}}}.")
            query = """
                    mutation KillChainPhaseEdit($id: ID!, $input: [EditInput]!) {
                        killChainPhaseEdit(id: $id) {
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
                result["data"]["killChainPhaseEdit"]["fieldPatch"]
            )
        self.opencti.log(
            "error",
            "[opencti_kill_chain] Missing parameters: id and key and value",
        )
        return None

    def delete(self, **kwargs):
        id_ = kwargs.get("id", None)
        if id_ is not None:
            self.opencti.log("info", f"Deleting Kill-Chain-Phase {{{id_}}}.")
            query = """
                 mutation KillChainPhaseEdit($id: ID!) {
                     killChainPhaseEdit(id: $id) {
                         delete
                     }
                 }
             """
            self.opencti.query(query, {"id": id_})
        self.opencti.log("error", "[opencti_kill_chain_phase] Missing parameters: id")
