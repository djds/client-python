# coding: utf-8
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

import magic

if TYPE_CHECKING:
    from ..api.opencti_api_client import File, OpenCTIApiClient


@dataclass
class ExternalReference:
    opencti: OpenCTIApiClient
    file: "File"
    properties: str = """
        id
        standard_id
        entity_type
        parent_types
        created_at
        updated_at
        created
        modified
        source_name
        description
        url
        hash
        external_id
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
    """

    def list(self, **kwargs):
        """
        List External-Reference objects

        :param filters: the filters to apply
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of External-Reference objects
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
            f"Listing External-Reference with filters {json.dumps(filters)}.",
        )
        query = (
            """
            query ExternalReferences($filters: [ExternalReferencesFiltering], $first: Int, $after: ID, $orderBy: ExternalReferencesOrdering, $orderMode: OrderingMode) {
                externalReferences(filters: $filters, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
            result["data"]["externalReferences"], with_pagination
        )

    def read(self, **kwargs):
        """
        Read a External-Reference object

        :param id: the id of the External-Reference
        :param filters: the filters to apply if no id provided
        :return External-Reference object
        """
        id_ = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        if id_ is not None:
            self.opencti.log("info", f"Reading External-Reference {{{id_}}}.")
            query = (
                """
                query ExternalReference($id: String!) {
                    externalReference(id: $id) {
                        """
                + self.properties
                + """
                    }
                }
            """
            )
            result = self.opencti.query(query, {"id": id_})
            return self.opencti.process_multiple_fields(
                result["data"]["externalReference"]
            )
        if filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            return None
        self.opencti.log(
            "error",
            "[opencti_external_reference] Missing parameters: id or filters",
        )
        return None

    def create(self, **kwargs):
        """
        Create a External Reference object

        :param source_name: the source_name of the External Reference
        :return External Reference object
        """
        stix_id = kwargs.get("stix_id", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        source_name = kwargs.get("source_name", None)
        url = kwargs.get("url", None)
        external_id = kwargs.get("external_id", None)
        description = kwargs.get("description", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if source_name is not None and url is not None:
            self.opencti.log("info", f"Creating External Reference {{{source_name}}}.")
            query = (
                """
                mutation ExternalReferenceAdd($input: ExternalReferenceAddInput) {
                    externalReferenceAdd(input: $input) {
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
                        "source_name": source_name,
                        "external_id": external_id,
                        "description": description,
                        "url": url,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self.opencti.process_multiple_fields(
                result["data"]["externalReferenceAdd"]
            )
        self.opencti.log(
            "error",
            "[opencti_external_reference] Missing parameters: source_name and url",
        )
        return None

    def add_file(self, **kwargs):
        """
        Upload a file in this External-Reference

        :param id: the Stix-Domain-Object id
        :param file_name
        :param data
        :return void
        """
        id_ = kwargs.get("id", None)
        file_name = kwargs.get("file_name", None)
        data = kwargs.get("data", None)
        mime_type = kwargs.get("mime_type", "text/plain")
        if id_ is not None and file_name is not None:
            final_file_name = os.path.basename(file_name)
            query = """
                mutation ExternalReferenceEdit($id: ID!, $file: Upload!) {
                    externalReferenceEdit(id: $id) {
                        importPush(file: $file) {
                            id
                            name
                        }
                    }
                }
             """
            if data is None:
                # pylint: disable-next=consider-using-with
                data = open(file_name, "rb")
                if file_name.endswith(".json"):
                    mime_type = "application/json"
                else:
                    mime_type = magic.from_file(file_name, mime=True)
            self.opencti.log(
                "info",
                f"Uploading a file {{{final_file_name}}} in Stix-Domain-Object {{{id_}}}.",
            )
            return self.opencti.query(
                query,
                {"id": id_, "file": (self.file(final_file_name, data, mime_type))},
            )
        self.opencti.log(
            "error",
            "[opencti_stix_domain_object] Missing parameters: id or file_name",
        )
        return None

    def update_field(self, **kwargs):
        """
        Update a External Reference object field

        :param id: the External Reference id
        :param input: the input of the field
        :return The updated External Reference object
        """
        id_ = kwargs.get("id", None)
        input_ = kwargs.get("input", None)
        if id_ is not None and input_ is not None:
            self.opencti.log("info", f"Updating External-Reference {{{id_}}}.")
            query = """
                    mutation ExternalReferenceEdit($id: ID!, $input: [EditInput]!) {
                        externalReferenceEdit(id: $id) {
                            fieldPatch(input: $input) {
                                id
                            }
                        }
                    }
                """
            result = self.opencti.query(query, {"id": id_, "input": input_})
            return self.opencti.process_multiple_fields(
                result["data"]["externalReferenceEdit"]["fieldPatch"]
            )
        self.opencti.log(
            "error",
            "[opencti_external_reference] Missing parameters: id and key and value",
        )
        return None

    # pylint: disable-next=redefined-builtin
    def delete(self, id):  # TODO: rename `id`
        self.opencti.log("info", f"Deleting External-Reference {id}...")
        query = """
             mutation ExternalReferenceEdit($id: ID!) {
                 externalReferenceEdit(id: $id) {
                     delete
                 }
             }
         """
        self.opencti.query(query, {"id": id})

    def list_files(self, **kwargs):
        id_ = kwargs.get("id", None)
        self.opencti.log(
            "info",
            f"Listing files of External-Reference {{ {id_} }}",
        )
        query = """
            query externalReference($id: String!) {
                externalReference(id: $id) {
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
        entity = self.opencti.process_multiple_fields(
            result["data"]["externalReference"]
        )
        return entity["importFiles"]
