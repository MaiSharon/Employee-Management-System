from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError

from dept_app import models
from dept_app.utils.bootstrap_NotUse import BootStrapModelForm


class UploadModelForm(forms.ModelForm):

    class Meta:
        model = models.Photo
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control-file"})

        }


def image_add(request):

    queryset = models.Photo.objects.all()
    form = UploadModelForm()

    if request.method == "POST":
        form = UploadModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/image/add/")

    context = {
        "form": form,
        "queryset": queryset
    }

    return render(request, "image.html", context)


def image_delete(request, nid):
    models.Photo.objects.filter(id=nid).delete()
    return redirect("/image/add/")

