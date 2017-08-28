import datetime
import json

from feds.settings import FEDS_SETTING_GROUPS, \
    FEDS_LABEL_PARAM, \
    FEDS_DATE_SETTING, FEDS_VALUE_PARAM, \
    FEDS_BOOLEAN_SETTING, \
    FEDS_BOOLEAN_VALUE_TRUE, \
    FEDS_INTEGER_SETTING, \
    FEDS_CHOICE_SETTING, FEDS_CHOICES_PARAM, \
    FEDS_CURRENCY_SETTING, \
    FEDS_FLOAT_SETTING, FEDS_FLOAT_DECIMALS_PARAM, \
    FEDS_FLOAT_DECIMALS_DEFAULT, \
    FEDS_AGGREGATE_MACHINE_NAME_SEPARATOR, FEDS_INTEGER_FIELD_SIZE_DEFAULT, \
    FEDS_FLOAT_FIELD_SIZE_DEFAULT, FEDS_CURRENCY_FIELD_SIZE_DEFAULT, \
    FEDS_MIN_PARAM, FEDS_MAX_PARAM, \
    FEDS_MACHINE_NAME_PARAM, \
    FEDS_DETERMINING_VALUE_PARAM, FEDS_VISIBILITY_TEST_PARAM, \
    FEDS_MIN_DATE, FEDS_DATE_FIELD_SIZE_DEFAULT
from helpers.model_helpers import check_field_type_known, stringify_date
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

    # Setting machine names, linked to their FedsXXXSetting instances.
    setting_machine_names = dict()

    # Setting visibility testers.
    setting_visibility_testers = dict()

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
        # Link machine name to self. Convenient lookup given machine name.
        FedsSetting.setting_machine_names[self.machine_name] = self
        # Use the label property if it is given, otherwise use the title
        # as the setting label.
        if FEDS_LABEL_PARAM in self.params:
            self.FEDS_LABEL_PARAM = self.params[FEDS_LABEL_PARAM]
        else:
            self.FEDS_LABEL_PARAM = self.title
        # Cache any visibility tests.
        if FEDS_VISIBILITY_TEST_PARAM in self.params:
            if FEDS_MACHINE_NAME_PARAM not in \
                    self.params[FEDS_VISIBILITY_TEST_PARAM]:
                message = FEDS_MACHINE_NAME_PARAM \
                          + ' missing from visibility dependency for "{title}".'
                raise KeyError(message.format(self.title))
            if FEDS_DETERMINING_VALUE_PARAM not in \
                    self.params[FEDS_VISIBILITY_TEST_PARAM]:
                message = FEDS_DETERMINING_VALUE_PARAM \
                          + ' missing from visibility dependency for "{title}".'
                raise KeyError(message.format(self.title))
            determiner_machine_name = self.params[FEDS_VISIBILITY_TEST_PARAM] \
                [FEDS_MACHINE_NAME_PARAM]
            determining_value = self.params[FEDS_VISIBILITY_TEST_PARAM] \
                [FEDS_DETERMINING_VALUE_PARAM]
            FedsSetting.setting_visibility_testers[self.machine_name] \
                = {
                    FEDS_MACHINE_NAME_PARAM: determiner_machine_name,
                    FEDS_DETERMINING_VALUE_PARAM: determining_value,
                  }

    @property
    def order(self):
        return self.__order

    @order.setter
    def order(self, order):
        self.__order = order

    def display_deets(self):
        return '<h2>Override me, the deeter.</h2>'

    def display_widget(self):
        validators = list()
        return '<h2>Override me, the widget.</h2>', validators

    def wrap_deets(self, html_to_wrap):
        """
        Wrap field-type-specific HTML in common container HTML
        :param html_to_wrap: HTML to wrap.
        :return: Wrapper HTML
        """
        if self.group == 'setting':
            panel_style = 'panel-default'
        elif self.group == 'anomaly':
            panel_style = 'panel-warning'
        else:
            message = 'wrap_deets: bad group "{group}" for "{title}"'
            raise ValueError(message.format(group=self.group, title=self.title))
        setting_title = self.group.capitalize()
        prepend_template = """
<div class="feds-setting panel {panel_style}">
    <div class="panel-heading feds-setting-header">
        {setting_title}
        <a onclick="showWidget({db_id}, '{machine_name}');return false;"
           href="#"
            class="feds-plain-text-link"><span
                class="glyphicon glyphicon-cog pull-right"
                aria-hidden="true"></span></a>
    </div>
    <div class="panel-body feds-setting-body">"""
        prepend = prepend_template.format(
            panel_style=panel_style,
            setting_title=setting_title,
            db_id=self.db_id,
            machine_name=self.machine_name,
        )
        postpend = """
    </div>
<div>
"""
        return prepend + html_to_wrap + postpend

    def html_hidden_machine_name(self):
        """
        Create HTML for a hidden widget that identifies
        a machine name.
        """
        result = '<input type="hidden" value="{machine_name}" ' \
                 'class="feds-widget-machine-name">'
        result = result.format(machine_name=self.machine_name)
        return result

    def display_description(self):
        """
        Create HTML to show setting description.
        :return: HTML.
        """
        template = """
            <div class='feds-setting-description'>
                {description}
            </div>
        """
        if self.description is None or self.description == '':
            return ''
        html = template.format(description=self.description)
        return html

    @classmethod
    def generate_js_settings_values_object(cls):
        """
        Return the values of the params in the settings in
        setting_machine_name() as a JS object.
        """
        result = '{\n'
        for machine_name, setting in cls.setting_machine_names.items():
            if FEDS_VALUE_PARAM in setting.params:
                result += '"{mn}": "{val}", \n'.format(
                    mn=machine_name,
                    val=setting.params[FEDS_VALUE_PARAM]
                )
        result += '}'
        return result

    @classmethod
    def generate_js_visibility_testers_object(cls):
        """
        Return visibility testers in a JS object.

        mn = machine name of the setting whose visibility is being controlled.
        dmn = machine name of the setting that controls visibility.
        dv = if dmn has this value, controlled setting is visible.

        dmn_key = key of the dmn in the JS object.
        dv_key = key of the dv in the JS object.
        """
        result = '{\n'
        for machine_name, determiner_pair \
                in cls.setting_visibility_testers.items():
            determiner = determiner_pair[FEDS_MACHINE_NAME_PARAM]
            determining_value = determiner_pair[FEDS_DETERMINING_VALUE_PARAM]
            entry = '''
                "{mn}": {{
                  "{dmn_key}":"{dmn}",
            "{dv_key}": "{dv}"
                }},
            '''
            entry = entry.format(
                mn=machine_name,
                dmn_key=FEDS_MACHINE_NAME_PARAM,
                dmn=determiner,
                dv_key=FEDS_DETERMINING_VALUE_PARAM,
                dv=determining_value,
            )
            result += entry
        result += '}'
        return result


class FedsDateSetting(FedsSetting):
    """
    A setting that is a date.
    """
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_DATE_SETTING
        if FEDS_VALUE_PARAM in self.params:
            if isinstance(self.params[FEDS_VALUE_PARAM], datetime.date):
                # Convert to string for JSON storage.
                self.params[FEDS_VALUE_PARAM] \
                    = stringify_date(self.params[FEDS_VALUE_PARAM])
            elif isinstance(self.params[FEDS_VALUE_PARAM], str):
                # Specs must be in Y/M/D.
                date_parts = self.params[FEDS_VALUE_PARAM].split('/')
                try:
                    d = datetime.date(int(date_parts[0]), int(date_parts[1]),
                                        int(date_parts[2]))
                except ValueError:
                    raise ValidationError('Dates must be in Y/M/D form.')
                # Convert min date from string to datetime.date
                date_parts = FEDS_MIN_DATE.split('/')
                min_d = datetime.date(int(date_parts[0]), int(date_parts[1]),
                                      int(date_parts[2]))
                # Test date against allowed min.
                if d < min_d:
                    message = 'Date "{d}" less than allowed min for "{title}".'
                    raise ValueError(message.format(d=d, title=self.title))
            else:
                message = 'Wrong data type, need str of date. For "{title}".'
                raise TypeError(message.format(title=self.title))
        # if FEDS_VALUE_PARAM in self.params:
        #     self.value = self.params[FEDS_VALUE_PARAM]

    def display_deets(self):
        """
        Create HTML to show a date.
        :return: HTML.
        """
        template = '''
            <div class="feds-date feds-setting-type" id="{machine_name}">
                <p>{label}</p>
                <p class="feds-value">{value}</p>
            </div>
        '''
        result = template.format(
            machine_name=self.machine_name,
            label=self.label,
            value=self.params[FEDS_VALUE_PARAM]
        ) + self.display_description()
        return result

    def display_widget(self):
        """
        Make a widget for date settings.
        """
        template = self.html_hidden_machine_name()
        template += '''
            <div class='feds-date-widget'>
                <label>
                    {label}
                    <input type="text" class="form-control {machine_name}"
                        size="{size}"
                        name="{machine_name}" 
                        value="{value}" autofocus>
                </label>
            </div>
        '''
        instantiated = template.format(
            label=self.label,
            size=FEDS_DATE_FIELD_SIZE_DEFAULT,
            machine_name=self.machine_name,
            value=self.params[FEDS_VALUE_PARAM],
        ) + self.display_description()
        validators = list()
        if FEDS_MIN_PARAM in self.params:
            validators.append(
                {
                    'testType': 'min',
                    'testDataType': 'date',
                    'testValue': self.params[FEDS_MIN_PARAM],
                    'errorMessage': 'Sorry, must be after {min}.'.format(
                        min=self.params[FEDS_MIN_PARAM])
                }
            )
        return instantiated, validators


class FedsBooleanSetting(FedsSetting):
    """
    A setting that is a boolean value.
    """
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_BOOLEAN_SETTING
        # if FEDS_VALUE_PARAM in self.params:
        #     self.value = \
        #         self.params[FEDS_VALUE_PARAM] == FEDS_BOOLEAN_VALUE_TRUE

    def display_deets(self):
        """
        Create HTML to show a boolean setting.
        :return: HTML.
        """
        if self.params[FEDS_VALUE_PARAM] == 'true':
            display_value = 'On'
            display_value_class = 'text-success'
        else:
            display_value = 'Off'
            display_value_class = 'text-danger'
        template = '''
            <div class="feds-boolean feds-setting-type" id="{machine_name}">
                <p>{label}</p>
                <p class="feds-value {display_value_class}">{display_value}</p>
            </div>
        '''
        result = template.format(
            machine_name=self.machine_name,
            label=self.label,
            display_value_class=display_value_class,
            display_value=display_value
        ) + self.display_description()
        return result

    def display_widget(self):
        """
        Make a checkbox widget for a boolean settings.
        """
        # Is the checkbox checked at the start?
        checked = ''
        if FEDS_VALUE_PARAM in self.params:
            value = self.params[FEDS_VALUE_PARAM].strip().lower()
            if value == FEDS_BOOLEAN_VALUE_TRUE:
                checked = 'checked'
        template = self.html_hidden_machine_name()
        template += '''
            <div class='feds-boolean-widget checkbox'>
                <label>
                    <input type="checkbox" 
                        id="{machine_name}" name="{machine_name}"
                        value="true" {checked} autofocus>
                    {label}
                </label>
            </div>
        '''
        instantiated = template.format(
            label=self.label,
            machine_name=self.machine_name,
            checked=checked,
            description=self.description,
        ) + self.display_description()
        # No validators.
        validators = list()
        return instantiated, validators


class FedsIntegerSetting(FedsSetting):
    """
    A setting that is an integer value.
    """
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_INTEGER_SETTING
        self.convert_value_to_int()

    def convert_value_to_int(self):
        # Convert value to right type.
        if FEDS_VALUE_PARAM in self.params:
            if isinstance(self.params[FEDS_VALUE_PARAM], str):
                self.params[FEDS_VALUE_PARAM] \
                    = int(self.params[FEDS_VALUE_PARAM])

    def display_deets(self):
        """
        Create HTML to show an integer setting.
        :return: HTML.
        """
        self.convert_value_to_int()
        template = '''
            <div class="feds-integer feds-setting-type" id="{machine_name}">
                <p>{label}</p>
                <p class="feds-value">{value}</p>
            </div>
        '''
        result = template.format(
            machine_name=self.machine_name,
            label=self.label, value=self.params[FEDS_VALUE_PARAM]
        ) + self.display_description()
        return result

    def display_widget(self):
        """
        Make an integer widget for integer settings.
        """
        self.convert_value_to_int()
        template = self.html_hidden_machine_name()
        template += '''
            <div class='feds-integer-widget'>
                <label>
                    {label}
                    <input type="text" class="form-control {machine_name}"
                        size="{size}"
                        name="{machine_name}" 
                        value="{value}" autofocus>
                </label>
            </div>
        '''
        instantiated = template.format(
            label=self.label,
            size=FEDS_INTEGER_FIELD_SIZE_DEFAULT,
            machine_name=self.machine_name,
            value=self.params[FEDS_VALUE_PARAM],
        ) + self.display_description()
        validators = list()
        if FEDS_MIN_PARAM in self.params:
            validators.append(
                {
                    'testType': 'min',
                    'testDataType': 'int',
                    'testValue': self.params[FEDS_MIN_PARAM],
                    'errorMessage': 'Sorry, must be at least {min}.'.format(
                        min=self.params[FEDS_MIN_PARAM])
                }
            )
        if FEDS_MAX_PARAM in self.params:
            validators.append(
                {
                    'testType': 'max',
                    'testDataType': 'int',
                    'testValue': self.params[FEDS_MAX_PARAM],
                    'errorMessage': 'Sorry, must be no more than {max}.'.format(
                        max=self.params[FEDS_MAX_PARAM])
                }
            )
        return instantiated, validators


class FedsChoiceSetting(FedsSetting):
    """
    A setting that is one of a set of choices.
    """
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
            # self.value = self.params[FEDS_VALUE_PARAM].strip().lower()
            # Is that an available choice?
            available = False
            for choice_item in self.params[FEDS_CHOICES_PARAM]:
                if choice_item[0] == self.params[FEDS_VALUE_PARAM]:
                    available = True
                    break
            if not available:
                raise ValidationError(
                    "Value '{v}' for choice setting '{t}' is not valid"
                        .format(v=self.params[FEDS_VALUE_PARAM], t=self.title)
                )

    def display_deets(self):
        """
        Create HTML to show a choice setting.
        :return: HTML.
        """
        template = '''
            <div class="feds-choice feds-setting-type" id="{machine_name}">
                <p>{label}</p>
                <p class="feds-value">{display_value}</p>                 
            </div>
        '''
        # Find the display name of the value.
        display_value = None
        for value_pair in self.params[FEDS_CHOICES_PARAM]:
            if value_pair[0] == self.params[FEDS_VALUE_PARAM]:
                display_value = value_pair[1]
                break
        if display_value is None:
            message = 'Value "{value}" not in choices for "{title}".'
            raise ValueError(message.format(value=self.params[FEDS_VALUE_PARAM],
                                            title=self.title))
        result = template.format(
            machine_name=self.machine_name,
            label=self.label,
            display_value=display_value
        ) + self.display_description()
        return result

    def display_widget(self):
        """
        Make a radio buttons for choice settings.
        """
        # Check that choices are defined.
        if FEDS_CHOICES_PARAM not in self.params:
            message = 'No choices defined for "{title}".'
            raise ValueError(message.format(title=self.title))
        # Check the setting's value is a valid choice.
        found = False
        for value_pair in self.params[FEDS_CHOICES_PARAM]:
            if value_pair[0] == self.params[FEDS_VALUE_PARAM]:
                found = True
                break
        if not found:
            message = 'Value "{value}" not in choices for "{title}".'
            raise ValueError(message.format(value=self.params[FEDS_VALUE_PARAM],
                                            title=self.title))
        # Make the radio buttons.
        radio_buttons_html = ''
        for value_pair in self.params[FEDS_CHOICES_PARAM]:
            radio_button_html = """
                <div class="radio">
                  <label>
                    <input type="radio" name="{machine_name}" 
                        value="{option_value}" {checked}>
                    {option_label}
                  </label>
                </div>            
            """
            # Is this the option currently chosen?
            checked = ''
            if value_pair[0] == self.params[FEDS_VALUE_PARAM]:
                checked = 'checked'
            # Make complete HTML for the option.
            radio_button_html = radio_button_html.format(
                machine_name=self.machine_name,
                option_value=value_pair[0],
                checked=checked,
                option_label=value_pair[1],
            )
            # Add the option's HTML to the group's HTML
            radio_buttons_html += radio_button_html
        template = self.html_hidden_machine_name()
        template += '''
            <p>{label}</p>
            <div class='feds-choices-widget'>
                {options}
            </div>
        '''
        instantiated = template.format(
            label=self.label,
            options=radio_buttons_html,
            description=self.description,
        ) + self.display_description()
        # No validators.
        validators = list()
        return instantiated, validators


class FedsCurrencySetting(FedsSetting):
    """
    A setting that is a currency value.
    """
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_CURRENCY_SETTING
        self.convert_value_to_currency()

    def convert_value_to_currency(self):
        # Convert value to right type.
        if FEDS_VALUE_PARAM in self.params:
            if isinstance(self.params[FEDS_VALUE_PARAM], str):
                self.params[FEDS_VALUE_PARAM] \
                    = float(self.params[FEDS_VALUE_PARAM])

    def display_deets(self):
        self.convert_value_to_currency()
        """
        Create HTML to show a currency setting.
        :return: HTML.
        """
        template = self.html_hidden_machine_name()
        template += '''
            <div class="feds-currency feds-setting-type" id="{machine_name}">
                <p>{label}</p>
                <p class="feds-value">{value}</p>
            </div>
        '''
        result = template.format(
            machine_name=self.machine_name,
            label=self.label, value=self.params[FEDS_VALUE_PARAM]
        ) + self.display_description()
        return result

    def display_widget(self):
        self.convert_value_to_currency()
        """
        Make a text widget for currency settings.
        """
        template = '''
            <div class='feds-float-widget'>
                <label>
                    {label}
                    $<input type="text" class="form-control"
                        size="{size}"
                        id="{machine_name}" name="{machine_name}" 
                        value="{value}" autofocus>
                </label>
            </div>
        '''
        instantiated = template.format(
            label=self.label,
            size=FEDS_CURRENCY_FIELD_SIZE_DEFAULT,
            machine_name=self.machine_name,
            value=self.params[FEDS_VALUE_PARAM],
        ) + self.display_description()
        validators = list()
        if FEDS_MIN_PARAM in self.params:
            validators.append(
                {
                    'testType': 'min',
                    'testDataType': 'currency',
                    'testValue': self.params[FEDS_MIN_PARAM],
                    'errorMessage': 'Sorry, must be at least {min}.'.format(
                        min=self.params[FEDS_MIN_PARAM])
                }
            )
        if FEDS_MAX_PARAM in self.params:
            validators.append(
                {
                    'testType': 'max',
                    'testDataType': 'currency',
                    'testValue': self.params[FEDS_MAX_PARAM],
                    'errorMessage': 'Sorry, must be no more than {max}.'.format(
                        max=self.params[FEDS_MAX_PARAM])
                }
            )
        return instantiated, validators


class FedsFloatSetting(FedsSetting):
    """
    A setting that is a currency value.
    """
    def __init__(self, db_id, title, description, machine_name,
                 group, params, setting_order):
        super().__init__(db_id, title, description, machine_name,
                         group, params, setting_order)
        self.type = FEDS_FLOAT_SETTING
        # if FEDS_VALUE_PARAM in self.params:
        #     self.value = self.params[FEDS_VALUE_PARAM]
        # Decimal places to show.
        self.decimals = FEDS_FLOAT_DECIMALS_DEFAULT
        if FEDS_FLOAT_DECIMALS_PARAM in self.params:
            self.decimals = self.params[FEDS_FLOAT_DECIMALS_PARAM]
        self.convert_value_to_float();

    def convert_value_to_float(self):
        # Convert value to right type.
        if FEDS_VALUE_PARAM in self.params:
            if isinstance(self.params[FEDS_VALUE_PARAM], str):
                self.params[FEDS_VALUE_PARAM] \
                    = float(self.params[FEDS_VALUE_PARAM])

    def display_deets(self):
        """
        Create HTML to show a float setting.
        :return: HTML.
        """
        self.convert_value_to_float()
        template = '''
            <div class="feds-float feds-setting-type" id="{machine_name}">
                <p>{label}</p>
                <p class="feds-value">{value}</p>
            </div>
        '''
        result = template.format(
            machine_name=self.machine_name,
            label=self.label,
            value=str(round(self.params[FEDS_VALUE_PARAM], self.decimals)),
        ) + self.display_description()
        return result

    def display_widget(self):
        """
        Make a text widget for float settings.
        """
        self.convert_value_to_float()
        template = self.html_hidden_machine_name()
        template += '''
            <div class='feds-float-widget'>
                <label>
                    {label}
                    <input type="text" class="form-control"
                        size="{size}"
                        id="{machine_name}" name="{machine_name}" 
                        value="{value}" autofocus>
                </label>
            </div>
        '''
        instantiated = template.format(
            label=self.label,
            size=FEDS_FLOAT_FIELD_SIZE_DEFAULT,
            machine_name=self.machine_name,
            value=self.params[FEDS_VALUE_PARAM],
        ) + self.display_description()
        validators = list()
        if FEDS_MIN_PARAM in self.params:
            validators.append(
                {
                    'testType': 'min',
                    'testDataType': 'float',
                    'testValue': self.params[FEDS_MIN_PARAM],
                    'errorMessage': 'Sorry, must be at least {min}.'.format(
                        min=self.params[FEDS_MIN_PARAM])
                }
            )
        if FEDS_MAX_PARAM in self.params:
            validators.append(
                {
                    'testType': 'max',
                    'testDataType': 'float',
                    'testValue': self.params[FEDS_MAX_PARAM],
                    'errorMessage': 'Sorry, must be no more than {max}.'.format(
                        max=self.params[FEDS_MAX_PARAM])
                }
            )
        return instantiated, validators
