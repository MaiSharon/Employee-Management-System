from django.shortcuts import render, redirect

from dept_app import models
from dept_app.utils.form import PrettyEditModelForm, PrettyModelForm


def pretty_list(request):

    ## 會帶著原來的搜索條件加上這裡自定義的搜索條件
    # print(request.GET)  # 可獲取到所有url上的值  <QueryDict: {'page': ['999'], 'xx': ['555']}>
    # request.GET.setlist('xx', 11)  # 會報錯，因request還有其他程式業務範圍要使用
    # 使用深度拷貝改一段字串就可以用了， 改這個query_dict._mutable = True
    # from django.http.request import QueryDict
    # import copy
    # query_dict = copy.deepcopy(request.GET)
    # query_dict._mutable = True
    # query_dict.setlist('xx', [11])
    # # 經過上面步驟後可由此處來傳遞參數給url，同時保留其他傳遞數值  page=999&xx=555&page=11
    # print(query_dict.urlencode())  # 獲取的值變成url可用  page=999&xx=555

    search_dict = {}
    search = request.GET.get("search", "")  # 預設為空字串，讓input不出現None保持乾淨空的

    # 0.2. 當GET在url有獲取到值
    if search:  # 0.2.1 True 將會把獲取值新增到字典
        search_dict["mobile__contains"] = search  # 字典鍵值的值的新增方式

    # 分頁組件化
    from dept_app.utils.pagination import Pagination

    # 把調數據傳給分頁組件的類
    queryset = models.PrettyNum.objects.filter(**search_dict).order_by("-level")

    if not queryset:
        print(search_dict, queryset)
        queryset = models.PrettyNum.objects.all().order_by("-level")

    page_object = Pagination(request, queryset)

    page = page_object.page
    # 2. 當前訪問的頁碼，默認為第1頁 也就是在網址輸入?=page
    # page = int(request.GET.get("page", 1))  # 1
    # page_size = 10  # 決定一頁中呈現多少條為數據
    # # 3. 起始值與結束值
    # start = (page - 1) * page_size  # 才會符合切片從0開始計算
    # end = page * page_size

    # 4 排序 -為倒序 (融入分頁)
    # queryset = models.PrettyNum.objects.filter(**search_dict).order_by("-level")[page_object.start:page_object.end]

    # 6. 數據庫的總數據量，也就是總共有多少條數據(已經融入排序)
    # total_count = models.PrettyNum.objects.filter(**search_dict).order_by("-level").count()

    # 7. 取得總頁碼數。取整數(商數)->總頁碼數、餘數->多出的數據也成一頁
    # total_page, page_other = divmod(total_count, page_size)
    # if page_other > 0:  # 如果餘數大於0也就是無法滿足page_size為完整一頁時，但數據也是要呈現出來
    #     total_page += 1

    # 8. 計算出當前頁的前五頁、後五頁(但有個問題沒有數據也會有-1透過8.2解決)，並控制在只有數據的範圍內
    # plus = 5  # 決定當前位置的前後各出現幾頁
    #
    # # 8.1 數據庫中的數據比較少，都沒有達到11頁
    # if total_page <= plus * 2 + 1:  # 11 ，如果之後網頁呈現頁碼數量要改的話，不用手動改此，改plus即可
    #     start_page = 1
    #     end_page = total_page
    #
    # # 8.2 數據庫中數據大於11頁
    # else:
    #     # 8.3 當前頁<5
    #     if page <= plus:  # 判斷當前頁碼
    #         start_page = 1
    #         end_page = plus * 2 + 1
    #
    #     # 8.4 當前頁+5 >總頁碼
    #     else:
    #         start_page = page - plus
    #         if (page + plus) > total_page:  # 判斷頁碼是否超出數據
    #             end_page = total_page
    #         else:
    #             end_page = page + plus
    #
    # page_str_list = []
    # n = "\n"
    # # 10. 頁碼首頁
    # home_page = f'<li class="page-item"><a class="page-link" href="?page={1}">首頁</a></li>'
    # page_str_list.append(home_page)
    #
    # # 9. 上一頁
    # if page > 1:
    #     prev_page = f'<li class="page-item"><a class="page-link" href="?page={page - 1}">上一頁</a></li>'
    # else:
    #     prev_page = f'<li class="page-item"><a class="page-link" href="?page={1}">上一頁</a></li>'
    # page_str_list.append(prev_page)
    #
    # # 5. 生成頁碼，做成列表且去除換行
    # for i in range(start_page, end_page+1):  # range是前取後不取因此記得要在原本數值上+1
    #     # 實現當前選取頁面 html裡面加上 active
    #     if i == page:
    #         page_list = f'<li class="page-item active" aria-current="page"><a class="page-link" href="?page={i}">{i}</a></li>'
    #     else:
    #         page_list = f'<li class="page-item"><a class="page-link" href="?page={i}">{i}</a></li>'
    #     page_str_list.append(page_list)
    #
    # # 9.1 下一頁
    # if page < total_page:
    #     next_page = f'<li class="page-item"><a class="page-link" href="?page={page + 1}">下一頁</a></li>'
    # else:
    #     next_page = f'<li class="page-item"><a class="page-link" href="?page={total_page}">下一頁</a></li>'
    # page_str_list.append(next_page)
    #
    # # 5-1. 由於生成是字串要讓html辨別是安全的，因此要導入from django.utils.safestring import mark_safe
    # page_string = mark_safe(f'{"".join(page_str_list)}{n}')

    context = {
        "search": search,
        "page": page,

        "queryset": page_object.page_queryset,  # 分完頁的數據條
        "page_string": page_object.html()  # 頁碼
    }

    return render(request, "pretty_list.html", context)


# class PrettyModelForm(forms.ModelForm):
#     hi = RegexValidator(r'^09', "手機號格式錯誤")
#     # 報錯提示方式一：正則表達式
#     mobile = forms.CharField(
#         label="手機號",
#         # 0開頭的並且要接3-9之間的數字，\d{8}為之後要接幾個數字。逗號後面為錯誤提示
#         # 可以輸入多個錯誤提示
#         validators=[RegexValidator(r'\d{8}$', "手機號碼長度錯誤"), hi]
#     )
#
#     class Meta:
#         model = models.PrettyNum
#         # fields = ["mobile", "price", "level", "status"]
#         fields = "__all__"  # 全部字段
#         # exclude = ["level"]  # 排除那些字段
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # 把Bootstrap的樣式貼上
#         for name, field in self.fields.items():
#             field.widget.attrs = {"class": "form-control", "placeholder": field.label}
#
#     # 報錯提示方式二：鉤子方法 記得導入from django.core.exceptions import ValidationError
#     # 只在數據新增的pretty_add使用
#     def clean_mobile(self):
#         txt_mobile = self.cleaned_data["mobile"]
#         exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
#         if exists:
#             raise ValidationError("手機號碼已經存在")
#
#         # 驗證通過，用戶輸入的值返回
#         return txt_mobile


def pretty_add(request):
    if request.method == "GET":
        form = PrettyModelForm()
        return render(request, "pretty_add.html", {'form': form})

    form = PrettyModelForm(data=request.POST)
    if form.is_valid():
        # 如果校驗成功，保存到數據庫
        form.save()
        return redirect("/pretty/list/")
    return render(request, "pretty_add.html", {"form": form})


# class PrettyEditModelForm(forms.ModelForm):
#     # 呈現方式一:直接移除該欄位
#     """
#         class Meta:
#         model = models.PrettyNum
#         fields = [ "price", "level", "status"]
#     """
#     # 呈現方式二:將該欄位設置成無法更改
#     mobile = forms.CharField(disabled=True, label="mobile")
#
#     class Meta:
#         model = models.PrettyNum
#         fields = ["mobile", "price", "level", "status"]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#         # 把Bootstrap的樣式貼上
#         for name, field in self.fields.items():
#             field.widget.attrs = {"class": "form-control", "placeholder": field.label}
#
#     # 只在編輯時使用pretty_edit
#     def clean_mobile(self):
#         txt_mobile = self.cleaned_data["mobile"]
#
#         # 1. exists() 判斷這數據是否存在 True/False
#         # 2. exclude() 排除當前的這數據的驗證，避免編輯時被此exists() 判斷這數據是否存在的邏輯衝突，而一直出現"手機號碼已存在"
#         exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
#         if exists:
#             raise ValidationError("手機號碼已經存在")
#
#         # 驗證通過，用戶輸入的值返回
#         return txt_mobile


def pretty_edit(request, nid):
    row_object = models.PrettyNum.objects.filter(id=nid).first()
    if request.method == "GET":
        form = PrettyEditModelForm(instance=row_object)
        return render(request, "pretty_edit.html", {"form": form})

    form = PrettyEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 如果校驗成功，保存到數據庫
        form.save()
        return redirect("/pretty/list/")
    return render(request, "pretty_edit.html", {"form": form})


def pretty_delete(request, nid):
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect("/pretty/list/")
