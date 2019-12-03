# coding: utf-8

import json
from pycti.utils.constants import CustomProperties


class CourseOfAction:
    def __init__(self, opencti):
        self.opencti = opencti
        self.properties = """
            id
            stix_id_key
            stix_label
            entity_type
            parent_types
            name
            alias
            description
            graph_data
            created
            modified            
            created_at
            updated_at
            createdByRef {
                node {
                    id
                    entity_type
                    stix_id_key
                    stix_label
                    name
                    alias
                    description
                    created
                    modified
                }
                relation {
                    id
                }
            }            
            markingDefinitions {
                edges {
                    node {
                        id
                        entity_type
                        stix_id_key
                        definition_type
                        definition
                        level
                        color
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }
            tags {
                edges {
                    node {
                        id
                        tag_type
                        value
                        color
                    }
                    relation {
                        id
                    }
                }
            }
            externalReferences {
                edges {
                    node {
                        id
                        entity_type
                        stix_id_key
                        source_name
                        description
                        url
                        hash
                        external_id
                        created
                        modified
                    }
                    relation {
                        id
                    }
                }
            }         
        """

    """
        List Course-Of-Action objects

        :param filters: the filters to apply
        :param search: the search keyword
        :param first: return the first n rows from the after ID (or the beginning if not set)
        :param after: ID of the first row for pagination
        :return List of Course-Of-Action objects
    """

    def list(self, **kwargs):
        filters = kwargs.get('filters', None)
        search = kwargs.get('search', None)
        first = kwargs.get('first', 500)
        after = kwargs.get('after', None)
        order_by = kwargs.get('orderBy', None)
        order_mode = kwargs.get('orderMode', None)
        self.opencti.log('info', 'Listing Course-Of-Actions with filters ' + json.dumps(filters) + '.')
        query = """
            query CourseOfActions($filters: [CourseOfActionsFiltering], $search: String, $first: Int, $after: ID, $orderBy: CoursesOfActionOrdering, $orderMode: OrderingMode) {
                courseOfActions(filters: $filters, search: $search, first: $first, after: $after, orderBy: $orderBy, orderMode: $orderMode) {
                    edges {
                        node {
                            """ + self.properties + """
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
        result = self.opencti.query(query, {'filters': filters, 'search': search, 'first': first, 'after': after, 'orderBy': order_by, 'orderMode': order_mode})
        return self.opencti.process_multiple(result['data']['courseOfActions'])

    """
        Read a Course-Of-Action object
        
        :param id: the id of the Course-Of-Action
        :param filters: the filters to apply if no id provided
        :return Course-Of-Action object
    """

    def read(self, **kwargs):
        id = kwargs.get('id', None)
        filters = kwargs.get('filters', None)
        if id is not None:
            self.opencti.log('info', 'Reading Course-Of-Action {' + id + '}.')
            query = """
                query CourseOfAction($id: String!) {
                    courseOfAction(id: $id) {
                        """ + self.properties + """
                    }
                }
             """
            result = self.opencti.query(query, {'id': id})
            return self.opencti.process_multiple_fields(result['data']['courseOfAction'])
        elif filters is not None:
            result = self.list(filters=filters)
            if len(result) > 0:
                return result[0]
            else:
                return None
        else:
            self.opencti.log('error', 'Missing parameters: id or filters')
            return None

    """
        Export an Course-Of-Action object in STIX2
    
        :param id: the id of the Course-Of-Action
        :return Course-Of-Action object
    """

    def to_stix2(self, **kwargs):
        id = kwargs.get('id', None)
        mode = kwargs.get('mode', 'simple')
        max_marking_definition_entity = kwargs.get('max_marking_definition_entity', None)
        entity = kwargs.get('entity', None)
        if id is not None and entity is None:
            entity = self.read(id=id)
        if entity is not None:
            course_of_action = dict()
            course_of_action['id'] = entity['stix_id_key']
            course_of_action['type'] = 'course-of-action'
            course_of_action['name'] = entity['name']
            if self.opencti.not_empty(entity['stix_label']):
                course_of_action['labels'] = entity['stix_label']
            else:
                course_of_action['labels'] = ['course-of-action']
            if self.opencti.not_empty(entity['description']): course_of_action['description'] = entity['description']
            course_of_action['created'] = self.opencti.stix2.format_date(entity['created'])
            course_of_action['modified'] = self.opencti.stix2.format_date(entity['modified'])
            if self.opencti.not_empty(entity['alias']): course_of_action[CustomProperties.ALIASES] = entity['alias']
            course_of_action[CustomProperties.ID] = entity['id']
            return self.opencti.stix2.prepare_export(entity, course_of_action, mode, max_marking_definition_entity)
        else:
            self.opencti.log('error', 'Missing parameters: id or entity')
