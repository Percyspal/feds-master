# https://opensourcehacker.com/2013/05/16/putting-breakpoints-to-html-templates-in-python/

# Useful lines
# Local vars?
# locals().keys()
# Context variables.
# for d in context.dicts: print (d.keys())
# Show attributes of field username in user_form.
# for i in context['user_form'].fields["username"].__dict__.items(): print(i)


import pdb as pdb_module
from django.template import Library, Node

register = Library()


class PdbNode(Node):

    def render(self, context):
        pdb_module.set_trace()
        return ''


@register.tag
def pdb(parser, token):
    return PdbNode()
