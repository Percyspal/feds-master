import json
from django.core.exceptions import ValidationError
from feds.settings import FEDS_DATE_RANGE_SETTING, FEDS_BOOLEAN_SETTING, \
    FEDS_INTEGER_SETTING, FEDS_CHOICE_SETTING, FEDS_CURRENCY_SETTING, \
    FEDS_FLOAT_SETTING
from helpers.model_helpers import is_legal_json, json_string_to_dict
from projects.internal_representation_classes import FedsDateRangeSetting, \
    FedsBooleanSetting, FedsIntegerSetting, FedsChoiceSetting, \
    FedsCurrencySetting, FedsFloatSetting


class SettingsGatherer:
    """
    Init the settings gather, passing it the settings lists, and the
    names of the relevant fields in the lists.
    :param base_settings: Data from FieldSettingsDb, that is the base data for
            each setting.
    :param relationship_settings: Data from the settings relatioship DB table.
    :param relationship_setting_id_field: Name of the setting id field
            in relationship_settings.
    :param relationship_setting_order_field: Name of the setting order
            field in relationship_settings.
    :param relationship_setting_params_field: Name of the params field
            in relationship_settings.
    """

    def __init__(self,
                 base_settings,
                 relationship_settings,
                 relationship_setting_id_field,
                 relationship_setting_order_field,
                 relationship_setting_params_field
                 ):
        self.base_settings_db = base_settings
        self.relationship_settings_db = relationship_settings
        self.relationship_setting_id_field_db = relationship_setting_id_field
        self.relationship_setting_order_field_db \
            = relationship_setting_order_field
        self.relationship_setting_params_field_db \
            = relationship_setting_params_field

    def gather_settings(self):
        result = list()
        # Loop over the relationship records for settings.
        # For each one, collect its attribs, add in data from
        # the base record, and make a FedsXXXObject.
        for rel_setting_db in self.relationship_settings_db:
            attribs = dict()
            db_id = rel_setting_db['id']
            # Find the base setting data.
            found = False
            for base_setting_db in self.base_settings_db:
                if base_setting_db['id'] == rel_setting_db[
                            self.relationship_setting_id_field_db]:
                    found = True
                    break
            if not found:
                message = 'gather_settings: base with id "{id}" not found.'
                raise ReferenceError(message.format(
                    id=rel_setting_db[self.relationship_setting_id_field_db])
                )
            # Collect attributes, with relation data overriding base.
            attribs['db_id'] = db_id
            attribs['group'] = base_setting_db['setting_group']
            attribs['type'] = base_setting_db['setting_type']
            attribs['setting_order'] = rel_setting_db[
                self.relationship_setting_order_field_db
            ]
            # Machine name comes from the relationship.
            attribs['machine_name'] = rel_setting_db['machine_name']
            # Merge params.
            # Get base params.
            base_params = base_setting_db['setting_params']
            base_params = json_string_to_dict(base_params)
            # Get relation params.
            relation_params = rel_setting_db[
                self.relationship_setting_params_field_db
            ]
            relation_params = json_string_to_dict(relation_params)
            # Merge, with relation params taking precedence.
            merged_params = {}
            merged_params.update(base_params)
            merged_params.update(relation_params)
            attribs['params'] = merged_params
            # Title and description can be overridden.
            attribs['title'] = base_setting_db['title']
            if 'title' in attribs['params']:
                attribs['title'] = attribs['params']['title']
            attribs['description'] = base_setting_db['description']
            if 'description' in attribs['params']:
                attribs['description'] = attribs['params']['description']
            # Make a FedsXXXSetting.
            setting = self.setting_factory(attribs)
            # Attach to settings list.
            result.append(setting)
        return result

    def merge_params(self, default_params, overriding_params):
        """
        Merge two sets of JSON params.
        :param default_params: Default params.
        :param overriding_params: Overriding params.
        :return: Merged params.
        :rtype: dict
        """
        merged_params = {}
        merged_params.update(default_params)
        merged_params.update(overriding_params)
        return merged_params

    def setting_factory(self, attribs):
        """
        Return a setting of the type specified in attribs['type'].

        :param attribs: Dict with setting data.
        :return: FedsXXXSetting
        """
        if attribs['type'] == FEDS_DATE_RANGE_SETTING:
            result = FedsDateRangeSetting(
                db_id=attribs['db_id'],
                title=attribs['title'],
                description=attribs['description'],
                machine_name=attribs['machine_name'],
                group=attribs['group'],
                params=attribs['params'],
                setting_order=attribs['setting_order']
            )
        elif attribs['type'] == FEDS_BOOLEAN_SETTING:
            result = FedsBooleanSetting(
                db_id=attribs['db_id'],
                title=attribs['title'],
                description=attribs['description'],
                machine_name=attribs['machine_name'],
                group=attribs['group'],
                params=attribs['params'],
                setting_order=attribs['setting_order']
            )
        elif attribs['type'] == FEDS_INTEGER_SETTING:
            result = FedsIntegerSetting(
                db_id=attribs['db_id'],
                title=attribs['title'],
                description=attribs['description'],
                machine_name=attribs['machine_name'],
                group=attribs['group'],
                params=attribs['params'],
                setting_order=attribs['setting_order']
            )
        elif attribs['type'] == FEDS_CHOICE_SETTING:
            result = FedsChoiceSetting(
                db_id=attribs['db_id'],
                title=attribs['title'],
                description=attribs['description'],
                machine_name=attribs['machine_name'],
                group=attribs['group'],
                params=attribs['params'],
                setting_order=attribs['setting_order']
            )
        elif attribs['type'] == FEDS_CURRENCY_SETTING:
            result = FedsCurrencySetting(
                db_id=attribs['db_id'],
                title=attribs['title'],
                description=attribs['description'],
                machine_name=attribs['machine_name'],
                group=attribs['group'],
                params=attribs['params'],
                setting_order=attribs['setting_order']
            )
        elif attribs['type'] == FEDS_FLOAT_SETTING:
            result = FedsFloatSetting(
                db_id=attribs['db_id'],
                title=attribs['title'],
                description=attribs['description'],
                machine_name=attribs['machine_name'],
                group=attribs['group'],
                params=attribs['params'],
                setting_order=attribs['setting_order']
            )
        else:
            message = 'setting_factory: "{title}" with bad setting ' \
                      'type: "{type}"'
            raise TypeError(
                message.format(
                    title=attribs['title'], type=attribs['type_code']
                )
            )
        return result
