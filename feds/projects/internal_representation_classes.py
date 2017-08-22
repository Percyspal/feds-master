import datetime
import json

from django.utils.text import slugify

from businessareas.models import BusinessAreaDb
from feds.settings import FEDS_SETTING_GROUPS, FEDS_BASIC_SETTING_GROUP, \
    FEDS_LABEL, FEDS_NOTIONAL_FIELD_TYPES, FEDS_MACHINE_NAME_PARAM, \
    FEDS_DATE_RANGE_SETTING, FEDS_MIN_START_DATE, FEDS_MIN_END_DATE, \
    FEDS_VALUE_PARAM, \
    FEDS_START_DATE_PARAM, FEDS_END_DATE_PARAM, \
    FEDS_BOOLEAN_SETTING, \
    FEDS_BOOLEAN_VALUE_TRUE, FEDS_BOOLEAN_VALUE_FALSE, \
    FEDS_INTEGER_SETTING, \
    FEDS_CHOICE_SETTING, FEDS_CHOICES_PARAM, \
    FEDS_CURRENCY_SETTING, \
    FEDS_FLOAT_SETTING, FEDS_FLOAT_DECIMALS_PARAM, FEDS_FLOAT_DECIMALS_DEFAULT, \
    FEDS_AGGREGATE_MACHINE_NAME_SEPARATOR
from helpers.model_helpers import check_field_type_known
from projects.models import ProjectDb
from django.core.exceptions import ValidationError

"""
These classes are used to create an internal (in-memory) representation of
a project. DB relationships are simplified to list() memberships. 
FieldSpec and FieldSetting reuse is flattened. Params are merged during 
this process.

The resulting representation is easier to use for rendering a project, and 
updating in small pieces as the user changes project, table, and field
settings. 

Classes are:

* FedsProject: represents a project.
* FedsNotionalTable: represents a notional table, like Invoices.
* FedsFieldSpec: represents a field in a notional table
* FedsXXXSetting: settings of different types: integer, currency,
  choices, others.

All instances know how to render themselves for display. Settings
know how to render input widgets, we well.
"""


class FedsBase:
    """
    Base class with common properties.

    Treat it as abstract. Don't instantiate.
    """

    # List of existing machine names.
    machine_name_list = list()

    def __init__(self, db_id, title, description, machine_name):
        self.db_id = db_id
        self.title = title
        self.description = description
        self.machine_name = machine_name

    @property
    def db_id(self):
        return self.__db_id

    @db_id.setter
    def db_id(self, db_id):
        if db_id is None or not isinstance(db_id, int):
            raise TypeError('Base db_id is the wrong type: {}'.format(db_id))
        if db_id < 1:
            raise ValueError('Base db_id is invalid: {}'.format(db_id))
        self.__db_id = db_id

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, title):
        if title is None or not isinstance(title, str):
            raise TypeError('Base title is wrong type: {}'.format(title))
        if title.strip() == '':
            raise ValueError('Base title is MT')
        self.__title = title

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, description):
        self.__description = description

    @property
    def machine_name(self):
        return self.__machine_name

    @machine_name.setter
    def machine_name(self, machine_name):
        if not isinstance(machine_name, str):
            raise TypeError('Strange machine not a string.')
        machine_name = machine_name.strip().lower()
        if machine_name == '':
            raise ValueError('Machine name empty: "{title}".'
                             .format(title=self.title))
        self.__machine_name = machine_name
        if FEDS_AGGREGATE_MACHINE_NAME_SEPARATOR in machine_name:
            message = 'Machine name "{mn}" cannot have separator char: "{sep}"'
            raise ValueError(
                message.format(
                    mn=machine_name,
                    sep=FEDS_AGGREGATE_MACHINE_NAME_SEPARATOR
                )
            )
        if machine_name in FedsBase.machine_name_list:
            message = 'Machine name "{mn}" already defined. Title: "{title}"'
            raise ValueError(message.format(mn=machine_name, title=self.title))
        FedsBase.machine_name_list.append(machine_name)

    def __del__(self):
        """ Remove machine name from list once object destroyed. """
        if hasattr(self, 'machine_name'):
            if self.machine_name in FedsBase.machine_name_list:
                FedsBase.machine_name_list.remove(self.machine_name)

    def display_deets(self):
        """ Display an HTML rep of the instance. """
        # Subclasses should override this method, but still call it.
        return '<h1>Override display_deets()!</h1>'


class FedsBaseWithSettingsList(FedsBase):
    """
    Add the ability to have settings to the base. About half of these classes
    have settings.
    """

    def __init__(self, db_id, title, description, machine_name):
        super().__init__(db_id, title, description, machine_name)
        self.settings = list()

    def add_setting(self, setting):
        """ Add a setting to the list. """
        if not isinstance(setting, FedsSetting):
            raise TypeError('Base settings: wrong type when adding: {}'
                            .format(setting))
        self.settings.append(setting)


class FedsBusinessArea(FedsBaseWithSettingsList):
    """ A business area. """

    def __init__(self, db_id, title, description, machine_name):
        super().__init__(db_id, title, description, machine_name)


class FedsProject(FedsBaseWithSettingsList):
    """ A user project. """

    def __init__(self, db_id, title, slug,
                 business_area, description, machine_name):
        super().__init__(db_id, title, description, machine_name)
        self.slug = slug
        self.business_area = business_area
        # Notional tables that are part of this project.
        self.notional_tables = list()

    @property
    def slug(self):
        return self.__slug

    @slug.setter
    def slug(self, slug):
        if slug is None or not isinstance(slug, str):
            raise TypeError('Project slug is wrong type: {}'.format(slug))
        if slug.strip() == '':
            raise ValueError('Project slug is MT')
        self.__slug = slug

    @property
    def business_area(self):
        return self.__business_area

    @business_area.setter
    def business_area(self, business_area):
        if business_area is None or not isinstance(
                business_area, FedsBusinessArea):
            raise TypeError('Project business_area is wrong type: {}'
                            .format(business_area))
        self.__business_area = business_area

    def add_notional_table(self, notional_table):
        """ Add a notional table to the list. """
        if not isinstance(notional_table, FedsNotionalTable):
            raise TypeError('Project: wrong type when adding: {}'
                            .format(notional_table))
        self.notional_tables.append(notional_table)


class FedsNotionalTable(FedsBaseWithSettingsList):
    """ A notional table for a user project. """

    def __init__(self, db_id, title, description, machine_name):
        super().__init__(db_id, title, description, machine_name)
        self.field_specs = list()

    def add_field_spec(self, field_spec):
        """ Add a field spec to the list. """
        if not isinstance(field_spec, FedsFieldSpec):
            raise TypeError('Notional table field specs: '
                            'wrong type when adding: {}'.format(field_spec))
        self.field_specs.append(field_spec)


class FedsFieldSpec(FedsBaseWithSettingsList):
    """ A field for a user project. In a notional table. """

    def __init__(self, db_id, title, field_type, description, machine_name):
        super().__init__(db_id, title, description, machine_name)
        self.field_type = field_type

    @property
    def field_type(self):
        return self.__field_type

    @field_type.setter
    def field_type(self, field_type_in):
        if field_type_in is None or not isinstance(field_type_in, str):
            raise TypeError('Field spec field type is wrong type: {}'
                            .format(field_type_in))
        if field_type_in.strip() == '':
            raise ValueError('Field spec field type is MT')
        if not check_field_type_known(field_type_in):
            raise ValueError('Field spec field type is unknown: {}'
                             .format(field_type_in))
        self.__field_type = field_type_in


class FedsSetting(FedsBase):
    """
    A setting that a project, table, or fieldspec can have.

    * Each setting has a data type, like int, daterange, or choice.
    * Each setting has a value. MT values are not allowed.

    Settings know how to display themselves as HTML for output, as
    do fieldspecs, notional tables, and projects. Settings
    also know how to make input widgets.

    Treat this as an abstract class. Don't instantiate it.
    """

    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name)
        if not isinstance(setting_order, int):
            message = 'Setting "{title}": order "{order}" not numeric.'
            raise TypeError(message.format(title=title, order=setting_order))
        self.setting_order = setting_order
        # Validate the group.
        # TODO: replace with cool comprehension?
        group_ok = False
        for group_tuple in FEDS_SETTING_GROUPS:
            if group == group_tuple[0]:
                group_ok = True
                break
        if not group_ok:
            raise ValidationError('Unknown setting group: {group}'
                                  .format(group=group))
        self.group = group
        # Use custom label if given, else use title.
        self.label = self.title
        # Decode params into a list.
        self.params = dict()
        if not params:
            # Nothing to do. Already an MT list.
            pass
        elif isinstance(params, dict):
            # Already a dictionary.
            self.params = params
        elif isinstance(params, str):
            try:
                self.params = json.loads(params)
            except ValueError:
                message = '"{title}": bad JSON: "{json}"'
                raise ValidationError(message.
                                      format(title=self.title, json=params)
                                      )
        else:
            message = '"{title}": bad params type'
            raise ValidationError(message.format(title=self.title))
        if FEDS_LABEL in self.params:
            self.label = self.params[FEDS_LABEL]

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self, order):
        self.__order = order


class FedsDateRangeSetting(FedsSetting):
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_DATE_RANGE_SETTING
        if FEDS_START_DATE_PARAM in self.params:
            # Specs must be in Y/M/D.
            date_parts = self.params['startdate'].slice('/')
            try:
                self.start_date \
                    = datetime.date(date_parts[0], date_parts[1], date_parts[2])
            except ValueError:
                raise ValidationError('Start dates must be in Y/M/D format.')
        else:
            self.start_date = FEDS_MIN_START_DATE
        if FEDS_END_DATE_PARAM in self.params:
            # Specs must be in Y/M/D.
            date_parts = self.params['enddate'].slice('/')
            try:
                self.end_date \
                    = datetime.date(date_parts[0], date_parts[1], date_parts[2])
            except ValueError:
                raise ValidationError('End dates must be in Y/M/D format.')
        else:
            self.end_date = FEDS_MIN_END_DATE
        if self.start_date < FEDS_MIN_START_DATE:
            self.start_date = FEDS_MIN_START_DATE
        if self.end_date < FEDS_MIN_END_DATE:
            self.end_date = FEDS_MIN_END_DATE

    def display_deets(self):
        template = '''
            <div class="feds-date-range" id="{machinename}">
                <div class="feds-daterange-start">Start: {start}</div>
                <div class="feds-daterange-end">End: {end}</div>
            </div>
        '''
        result = template.format(
            machinename=self.machine_name,
            start=self.start_date, end=self.end_date)
        return result


class FedsBooleanSetting(FedsSetting):
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_BOOLEAN_SETTING
        if FEDS_VALUE_PARAM in self.params:
            self.value = \
                self.params[FEDS_VALUE_PARAM] == FEDS_BOOLEAN_VALUE_TRUE

    def display_deets(self):
        template = '''
            <div class="feds-boolean" id="{machinename}">
                {label} <span class="glyphicon glyphicon-{icon} pull-right" 
                    aria-hidden="true" title="{value}"></span>
            </div>
        '''
        if self.value:
            icon = 'ok-circle'
            value_title = 'On'
        else:
            icon = 'remove-circle'
            value_title = 'Off'
        result = template.format(
            machinename=self.machine_name,
            label=self.label, icon=icon, value=value_title)
        return result


class FedsIntegerSetting(FedsSetting):
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_INTEGER_SETTING
        if FEDS_VALUE_PARAM in self.params:
            self.value = self.params[FEDS_VALUE_PARAM]

    def display_deets(self):
        template = '''
            <div class="feds-integer" id="{machinename}">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(
            machinename=self.machine_name,
            label=self.label, value=self.value)
        return result


class FedsChoiceSetting(FedsSetting):
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_CHOICE_SETTING
        # Are there choices?
        if FEDS_CHOICES_PARAM not in self.params:
            raise ValidationError(
                'No choices for choice setting: {t}'.format(t=self.title)
            )
        # Is the choice made recorded?
        if FEDS_VALUE_PARAM in self.params:
            self.value = self.params[FEDS_VALUE_PARAM].strip().lower()
            # Is that an available choice?
            available = False
            for choice_item in self.params[FEDS_CHOICES_PARAM]:
                if choice_item[0] == self.value:
                    available = True
                    break
            if not available:
                raise ValidationError(
                    "Value '{v}' for choice setting '{t}' is not valid"
                        .format(v=self.params[FEDS_VALUE_PARAM], t=self.title)
                )

    def display_deets(self):
        template = '''
            <div class="feds-choice" id="{machinename}">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(
            machinename=self.machine_name,
            label=self.label, value=self.value)
        return result


class FedsCurrencySetting(FedsSetting):
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_CURRENCY_SETTING
        if FEDS_VALUE_PARAM in self.params:
            self.value = self.params[FEDS_VALUE_PARAM]

    def display_deets(self):
        template = '''
            <div class="feds-choice" id="{machinename}">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(
            machinename=self.machine_name,
            label=self.label, value=self.value)
        return result


class FedsFloatSetting(FedsSetting):
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_FLOAT_SETTING
        if FEDS_VALUE_PARAM in self.params:
            self.value = self.params[FEDS_VALUE_PARAM]
        # Decimal places to show.
        self.decimals = FEDS_FLOAT_DECIMALS_DEFAULT
        if FEDS_FLOAT_DECIMALS_PARAM in self.params:
            self.decimals = self.params[FEDS_FLOAT_DECIMALS_PARAM]

    def display_deets(self):
        template = '''
            <div class="feds-float" id="{machinename}">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(
            machinename=self.machine_name,
            label=self.label,
            value=str(round(self.value, self.decimals)),
        )
        return result
