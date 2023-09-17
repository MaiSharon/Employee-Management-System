from django import forms
from django.forms import Select


class BootStrap:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # name是指變量名稱可到models.py查看、field是指對象
        for name, field in self.fields.items():
            # 檢查widget的類型
            if isinstance(field.widget, Select):
                # 自定義select的class
                field.widget.attrs["class"] = "form-select"
            else:
                if field.widget.attrs:
                    field.widget.attrs["class"] = "form-control"
                else:
                    field.widget.attrs = {
                        "class": "form-control",
                    }


class BootStrapModelForm(BootStrap, forms.ModelForm):
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass

