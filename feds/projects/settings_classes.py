import datetime
from django.core.exceptions import ImproperlyConfigured
from feds.settings import FEDS_SETTING_GROUPS, FEDS_BASIC_SETTING_GROUP, \
    FEDS_LABEL, FEDS_FIELD_TYPES, \
    FEDS_DATE_RANGE_SETTING, FEDS_MIN_START_DATE, FEDS_MIN_END_DATE, \
    FEDS_VALUE_PARAM, \
    FEDS_START_DATE_PARAM, FEDS_END_DATE_PARAM, \
    FEDS_BOOLEAN_SETTING, \
    FEDS_BOOLEAN_VALUE_TRUE, FEDS_BOOLEAN_VALUE_FALSE, \
    FEDS_INTEGER_SETTING, \
    FEDS_CHOICE_SETTING, FEDS_CHOICES_PARAM, \
    FEDS_CURRENCY_SETTING
from projects.models import Project


class FedsBase:
    """ Base class with common properties. """

    def __init__(self, db_id, title, description):
        self.db_id = db_id
        self.title = title
        self.description = description
        self.settings = list()

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

    def add_setting(self, setting):
        """ Add a setting to the list. """
        if not isinstance(setting, FedsSetting):
            raise TypeError('Base settings: wrong type when adding: {}'
                            .format(setting))
        self.settings.append(setting)


class FedsProject(FedsBase):
    """ A user project. """

    def __init__(self, db_id, title, description, slug, business_area):
        super().__init__(db_id, title, description)
        self.slug = slug
        self.business_area = business_area
        # Notional tables that are part of this project.
        self.notional_tables = list()

    @property
    def slug(self):
        return self.__slug

    @slug.setter
    def slug(self, slug):
        if slug is None or not isinstance(slug ,str):
            raise TypeError('Project slug is wrong type: {}'.format(slug))
        if slug.strip() == '':
            raise ValueError('Project slug is MT')
        self.__slug = slug

    @property
    def business_area(self):
        return self.__business_area

    @business_area.setter
    def business_area(self, business_area):
        if business_area is None or not isinstance(business_area, int):
            raise TypeError('Project business_area is wrong type: {}'
                            .format(business_area))
        if business_area < 1:
            raise ValueError('Project business_area is invalid: {}'
                             .format(business_area))
        self.__business_area = business_area

    def add_notional_table(self, notional_table):
        """ Add a notional table to the list. """
        if not isinstance(notional_table, FedsNotionalTable):
            raise TypeError('Project: wrong type when adding: {}'
                            .format(notional_table))
        self.notional_tables.append(notional_table)


class FedsNotionalTable(FedsBase):
    """ A notional table for a user project. """

    def __init__(self, db_id, title, description):
        super().__init__(db_id, title, description)
        self.field_specs = list()

    def add_field_spec(self, field_spec):
        """ Add a field spec to the list. """
        if not isinstance(field_spec, FedsFieldSpec):
            raise TypeError('Notional table field specs: '
                            'wrong type when adding: {}'.format(field_spec))
        self.field_specs.append(field_spec)


class FedsFieldSpec(FedsBase):
    """ A field for a user project. In a notional table. """

    def __init__(self, db_id, title, description, field_type):
        super().__init__(db_id, title, description)
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
        # Check whether type is in valid list.
        valid = False
        for type_label, type_desc in FEDS_FIELD_TYPES:
            if type_label == field_type_in:
                valid = True
                break
        if not valid:
            raise ValueError('Field spec field type is unknown: {}'
                             .format(field_type_in))
        self.__field_type = field_type_in


class FedsSetting:
    def __init__(self, title='MT',
                 description='MT',
                 group=FEDS_BASIC_SETTING_GROUP):
        self.title = title
        self.description = description
        group_ok = False
        for group_tuple in FEDS_SETTING_GROUPS:
            if group == group_tuple[0]:
                group_ok = True
                break
        if not group_ok:
            raise ImproperlyConfigured('Unknown setting group: {group}'
                                       .format(group=group))
        self.group = group
        # Use custom label if given, else use title.
        self.label = self.title
        if hasattr(self, 'params'):
            if FEDS_LABEL in self.params:
                self.label = self.params[FEDS_LABEL]

    def display_deets(self):
        # Subclasses should override this method, but still call it.
        return '<h1>Override display_deets()!</h1>'


class FedsDateRangeSetting(FedsSetting):
    def __init__(self, title='MT', description='MT',
                 group=FEDS_BASIC_SETTING_GROUP, params={}):
        super().__init__(title, description, group)
        self.type = FEDS_DATE_RANGE_SETTING
        self.params = params
        if FEDS_START_DATE_PARAM in params:
            # Specs must be in Y/M/D.
            date_parts = params['startdate'].slice('/')
            try:
                self.start_date \
                    = datetime.date(date_parts[0], date_parts[1], date_parts[2])
            except ValueError:
                raise ImproperlyConfigured(
                    'Start dates must be in Y/M/D format.')
        else:
            self.start_date = FEDS_MIN_START_DATE
        if FEDS_END_DATE_PARAM in params:
            # Specs must be in Y/M/D.
            date_parts = params['enddate'].slice('/')
            try:
                self.end_date \
                    = datetime.date(date_parts[0], date_parts[1], date_parts[2])
            except ValueError:
                raise ImproperlyConfigured(
                    'End dates must be in Y/M/D format.')
        else:
            self.end_date = FEDS_MIN_END_DATE
        if self.start_date < FEDS_MIN_START_DATE:
            self.start_date = FEDS_MIN_START_DATE
        if self.end_date < FEDS_MIN_END_DATE:
            self.end_date = FEDS_MIN_END_DATE

    def display_deets(self):
        template = '''
            <div class="feds-date-range">
                <div class="feds-daterange-start">Start: {start}</div>
                <div class="feds-daterange-end">End: {end}</div>
            </div>
        '''
        result = template.format(start=self.start_date, end=self.end_date)
        return result


class FedsBooleanSetting(FedsSetting):
    def __init__(self, title='MT', description='MT',
                 group=FEDS_BASIC_SETTING_GROUP, params={}):
        super().__init__(title, description, group)
        self.params = params
        self.type = FEDS_BOOLEAN_SETTING
        if FEDS_VALUE_PARAM not in params:
            raise ImproperlyConfigured(
                'No value for boolean setting: {title}'.format(title=self.title)
            )
        self.value = \
            params[FEDS_VALUE_PARAM] == FEDS_BOOLEAN_VALUE_TRUE

    def display_deets(self):
        template = '''
            <div class="feds-boolean">
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
        result = template.format(label=self.label, icon=icon, value=value_title)
        return result


class FedsIntegerSetting(FedsSetting):
    def __init__(self, title='MT', description='MT',
                 group=FEDS_BASIC_SETTING_GROUP, params={}):
        super().__init__(title, description, group)
        self.params = params
        self.type = FEDS_INTEGER_SETTING
        if FEDS_VALUE_PARAM not in params:
            raise ImproperlyConfigured(
                'No value for integer setting: {title}'.format(title=self.title)
            )
        self.value = params[FEDS_VALUE_PARAM]

    def display_deets(self):
        template = '''
            <div class="feds-integer">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(label=self.label, value=self.value)
        return result


class FedsChoiceSetting(FedsSetting):
    def __init__(self, title='MT', description='MT',
                 group=FEDS_BASIC_SETTING_GROUP, params={}):
        super().__init__(title, description, group)
        self.params = params
        self.type = FEDS_CHOICE_SETTING
        # Are there choices?
        if FEDS_CHOICES_PARAM not in params:
            raise ImproperlyConfigured(
                'No choices for choice setting: {t}'.format(t=self.title)
            )
        # Is the choice made recorded?
        if FEDS_VALUE_PARAM not in params:
            raise ImproperlyConfigured(
                'No choice for choice setting: {t}'.format(t=self.title)
            )
        # Is that an available choice?
        if params[FEDS_VALUE_PARAM] not in params[FEDS_CHOICES_PARAM]:
            raise ImproperlyConfigured(
                "Value '{v}' for choice setting '{t}' is not valid"
                    .format(v=params[FEDS_VALUE_PARAM], t=self.title)
            )
        # OK.
        self.value = params[FEDS_VALUE_PARAM]

    def display_deets(self):
        template = '''
            <div class="feds-choice">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(label=self.label, value=self.value)
        return result


class FedsCurrencySetting(FedsSetting):
    def __init__(self, title='MT', description='MT',
                 group=FEDS_BASIC_SETTING_GROUP, params={}):
        super().__init__(title, description, group)
        self.params = params
        self.type = FEDS_CURRENCY_SETTING
        if FEDS_VALUE_PARAM not in params:
            raise ImproperlyConfigured(
                'No value for currency setting: {t}'.format(t=self.title)
            )
        # OK.
        self.value = params[FEDS_VALUE_PARAM]

    def display_deets(self):
        template = '''
            <div class="feds-choice">
                {label} <span class="pull-right">{value}</span>
            </div>
        '''
        result = template.format(label=self.label, value=self.value)
        return result
