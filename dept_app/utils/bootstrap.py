from django import forms


class BootStrap:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # name是指變量名稱可到models.py查看、field是指對象
        for name, field in self.fields.items():

            # 字段中有屬性，保留原有的屬性，沒有屬性，才增加
            if field.widget.attrs:  # 若字段中有屬性
                field.widget.attrs["class"] = "form-control"
                # field.widget.attrs["placeholder"] = field.label
            else:  # 若字段中沒有屬性
                field.widget.attrs = {
                    "class": "form-control",
                    # "placeholder": field.label
                }


class BootStrapModelForm(BootStrap, forms.ModelForm):
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass

