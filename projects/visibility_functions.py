from .internal_representation_classes import FedsSetting
from feds.settings import FEDS_NORMAL_DISTRIBUTION, FEDS_VALUE_PARAM

"""
These functions return True or False, showing whether a setting should
appear or not. The functions are linked to settings through their

parameters. See db_initializer for examples. Look for
FEDS_PYTHON_VISIBILITY_FUNCTION_PARAM.

"""


def feds_show_invoice_total_bt_mean(mean_setting):
    """
    The setting for normal distribution mean for total cost
    before tax should only be shown when the user has chosen to
    use a normal distribution.
    """
    # What distribution did the user choose?
    distribution_chosen = FedsSetting.get_param(
        'stat_dist_total_before_tax',
        FEDS_VALUE_PARAM
    )
    # Return True if it's normal.
    return distribution_chosen == FEDS_NORMAL_DISTRIBUTION
