from django.forms import ModelChoiceField

class ModelChoiceFieldWithLabel(ModelChoiceField):
    def __init__(self,
                 queryset,
                 empty_label="---------",
                 custom_label=None,
                 required=True,
                 widget=None,
                 label=None,
                 initial=None,
                 help_text='',
                 to_field_name=None,
                 limit_choices_to=None,
                 *args, **kwargs):
        super().__init__(queryset,
                         empty_label,
                         required,
                         widget,
                         label,
                         initial,
                         help_text,
                         to_field_name,
                         limit_choices_to,
                         *args, **kwargs)
        self.custom_label = custom_label

    def label_from_instance(self, obj):
        if self.custom_label:
            return self.custom_label(obj)
        else:
            return super().label_from_instance(obj)
