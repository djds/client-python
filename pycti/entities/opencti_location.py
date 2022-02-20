# coding: utf-8
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api.opencti_api_client import OpenCTIApiClient


@dataclass
class Location:
    opencti: OpenCTIApiClient
    properties = """
        id
        standard_id
        entity_type
        parent_types
        spec_version
        created_at
        updated_at
        createdBy {
            ... on Identity {
                id
                standard_id
                entity_type
                parent_types
                spec_version
                identity_class
                name
                description
                roles
                contact_information
                x_opencti_aliases
                created
                modified
                objectLabel {
                    edges {
                        node {
                            id
                            value
                            color
                        }
                    }
                }
            }
            ... on Organization {
                x_opencti_organization_type
                x_opencti_reliability
            }
            ... on Individual {
                x_opencti_firstname
                x_opencti_lastname
            }
        }
        objectMarking {
            edges {
                node {
                    id
                    standard_id
                    entity_type
                    definition_type
                    definition
                    created
                    modified
                    x_opencti_order
                    x_opencti_color
                }
            }
        }
        objectLabel {
            edges {
                node {
                    id
                    value
                    color
                }
            }
        }
        externalReferences {
            edges {
                node {
                    id
                    standard_id
                    entity_type
                    source_name
                    description
                    url
                    hash
                    external_id
                    created
                    modified
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
        }
        revoked
        confidence
        created
        modified
        name
        description
        latitude
        longitude
        precision
        x_opencti_aliases
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
        List Location objects

        :param types: the list of types
        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Location objects
        """
        types = kwargs.get("types", None)
        filters = kwargs.get("filters", None)
        search = kwargs.get("search", None)
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
            "info", f"Listing Locations with filters {json.dumps(filters)}."
        )
        query = (
            """
            query Locations($types: [String], $filters: [LocationsFiltering], $search: String, $first: Int, $after: ID, $orderBy: LocationsOrdering, $orderMode: OrderingMode) {
                locations(types: $types, filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
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
                "types": types,
                "filters": filters,
                "search": search,
                "first": first,
                "after": after,
                "orderBy": order_by,
                "orderMode": order_mode,
            },
        )
        return self.opencti.process_multiple(
            result["data"]["locations"], with_pagination
        )

    def read(self, **kwargs):
        """
        Read a Location object

        :param id: the id of the Location
        :param filters: the filters to apply if no id provided
        :return Location object
        """
        id_ = kwargs.get("id", None)
        filters = kwargs.get("filters", None)
        custom_attributes = kwargs.get("customAttributes", None)
        if id_ is not None:
            self.opencti.log("info", f"Reading Location {{{id_}}}.")
            query = (
                """
                query Location($id: String!) {
                    location(id: $id) {
                        """
                + (
                    custom_attributes
                    if custom_attributes is not None
                    else self.properties
                )
                + """
                    }
                }
             """
            )
            result = self.opencti.query(query, {"id": id_})
            return self.opencti.process_multiple_fields(result["data"]["location"])
        if filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            return None
        self.opencti.log(
            "error", "[opencti_location] Missing parameters: id or filters"
        )
        return None

    def create(self, **kwargs):
        """
        Create a Location object

        :param name: the name of the Location
        :return Location object
        """
        type_ = kwargs.get("type", None)
        stix_id = kwargs.get("stix_id", None)
        created_by = kwargs.get("createdBy", None)
        object_marking = kwargs.get("objectMarking", None)
        object_label = kwargs.get("objectLabel", None)
        external_references = kwargs.get("externalReferences", None)
        revoked = kwargs.get("revoked", None)
        confidence = kwargs.get("confidence", None)
        lang = kwargs.get("lang", None)
        created = kwargs.get("created", None)
        modified = kwargs.get("modified", None)
        name = kwargs.get("name", None)
        description = kwargs.get("description", "")
        latitude = kwargs.get("latitude", None)
        longitude = kwargs.get("longitude", None)
        precision = kwargs.get("precision", None)
        x_opencti_aliases = kwargs.get("x_opencti_aliases", None)
        x_opencti_stix_ids = kwargs.get("x_opencti_stix_ids", None)
        update = kwargs.get("update", False)

        if name is not None:
            self.opencti.log("info", f"Creating Location {{{name}}}.")
            query = """
                mutation LocationAdd($input: LocationAddInput) {
                    locationAdd(input: $input) {
                        id
                        standard_id
                        entity_type
                        parent_types
                    }
                }
            """
            result = self.opencti.query(
                query,
                {
                    "input": {
                        "type": type_,
                        "stix_id": stix_id,
                        "createdBy": created_by,
                        "objectMarking": object_marking,
                        "objectLabel": object_label,
                        "externalReferences": external_references,
                        "revoked": revoked,
                        "confidence": confidence,
                        "lang": lang,
                        "created": created,
                        "modified": modified,
                        "name": name,
                        "description": description,
                        "latitude": latitude,
                        "longitude": longitude,
                        "precision": precision,
                        "x_opencti_aliases": x_opencti_aliases,
                        "x_opencti_stix_ids": x_opencti_stix_ids,
                        "update": update,
                    }
                },
            )
            return self.opencti.process_multiple_fields(result["data"]["locationAdd"])
        self.opencti.log("error", "Missing parameters: name")
        return None

    def import_from_stix2(self, **kwargs):
        """
        Import an Location object from a STIX2 object

        :param stixObject: the Stix-Object Location
        :return Location object
        """
        stix_object = kwargs.get("stixObject", None)
        extras = kwargs.get("extras", {})
        update = kwargs.get("update", False)
        if "name" in stix_object:
            name = stix_object["name"]
        elif "city" in stix_object:
            name = stix_object["city"]
        elif "country" in stix_object:
            name = stix_object["country"]
        elif "region" in stix_object:
            name = stix_object["region"]
        else:
            self.opencti.log("error", "[opencti_location] Missing name")
            return None
        if "x_opencti_location_type" in stix_object:
            type_ = stix_object["x_opencti_location_type"]
        else:
            if "city" in stix_object:
                type_ = "City"
            elif "country" in stix_object:
                type_ = "Country"
            elif "region" in stix_object:
                type_ = "Region"
            else:
                type_ = "Position"
        if stix_object is not None:
            return self.create(
                type=type_,
                stix_id=stix_object["id"],
                createdBy=extras["created_by_id"]
                if "created_by_id" in extras
                else None,
                objectMarking=extras["object_marking_ids"]
                if "object_marking_ids" in extras
                else [],
                objectLabel=extras["object_label_ids"]
                if "object_label_ids" in extras
                else [],
                externalReferences=extras["external_references_ids"]
                if "external_references_ids" in extras
                else [],
                revoked=stix_object["revoked"] if "revoked" in stix_object else None,
                confidence=stix_object["confidence"]
                if "confidence" in stix_object
                else None,
                lang=stix_object["lang"] if "lang" in stix_object else None,
                created=stix_object["created"] if "created" in stix_object else None,
                modified=stix_object["modified"] if "modified" in stix_object else None,
                name=name,
                description=self.opencti.stix2.convert_markdown(
                    stix_object["description"]
                )
                if "description" in stix_object
                else "",
                latitude=stix_object["latitude"] if "latitude" in stix_object else None,
                longitude=stix_object["longitude"]
                if "longitude" in stix_object
                else None,
                precision=stix_object["precision"]
                if "precision" in stix_object
                else None,
                x_opencti_stix_ids=stix_object["x_opencti_stix_ids"]
                if "x_opencti_stix_ids" in stix_object
                else None,
                x_opencti_aliases=self.opencti.stix2.pick_aliases(stix_object),
                update=update,
            )
        self.opencti.log("error", "[opencti_location] Missing parameters: stixObject")
        return None
