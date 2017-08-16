import datetime
from django.core.exceptions import ImproperlyConfigured
from feds.settings import FEDS_DATE_RANGE_SETTING, FEDS_BOOLEAN_SETTING, \
    FEDS_SETTING_GROUPS, FEDS_BASIC_SETTING_GROUP, \
    FEDS_MIN_START_DATE, FEDS_MIN_END_DATE, \
    FEDS_START_DATE_PARAM, FEDS_END_DATE_PARAM, FEDS_LABEL, \
    FEDS_BOOLEAN_VALUE_PARAM, FEDS_BOOLEAN_VALUE_TRUE, FEDS_BOOLEAN_VALUE_FALSE


class FedsSetting:
    def __init__(self, title='MT',
                 description='MT',
                 group=FEDS_BASIC_SETTING_GROUP):
        self.title = title
        self.description = description
        self.group = group
        group_ok = False
        for group_tuple in FEDS_SETTING_GROUPS:
            if self.group == group_tuple[0]:
                group_ok = True
                break
        if not group_ok:
            raise ImproperlyConfigured('Unknown setting group: {group}'
                                       .format(group=self.group))

    def display_deets(self):
        # Subclasses should override this method.
        return '<h1>Override display_deets()!</h1>'

    # def display(self):
    #     result = self.display_opening() + self.display_title_desc() \
    #              + self.display_deets() + self.display_closing()
    #     return result


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
        # Use custom label if given, else use title.
        if FEDS_LABEL in params:
            self.label = params[FEDS_LABEL]
        else:
            self.label = title
        if FEDS_BOOLEAN_VALUE_PARAM not in params:
            raise ImproperlyConfigured(
                'No value for boolean setting: {title}'.format(title=self.title)
            )
        self.value = \
            params[FEDS_BOOLEAN_VALUE_PARAM] == FEDS_BOOLEAN_VALUE_TRUE

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
