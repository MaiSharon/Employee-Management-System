"""
自定義的分頁組件

在視圖函數中:
    def pretty_list(request):

        # 1.根據自己的情況去篩選自己的數據
        total_count = models.PrettyNum.objects.all()

        # 2.實力化分頁對象
        page_object = Pagination(request, queryset)

        context = {
        "search": search,

        "queryset": page_object.page_queryset,  # 分完頁的數據
        "page_string": page_object.html()  # 頁碼
        }

在html中
    {% for item in queryset%}
        <td scope="row">{{ item.id }}</td>
        <td>{{ item.mobile }}</td>
        <td>{{ item.price }}</td>
        <td>{{ item.get_level_display }}</td>
        <td>{{ item.get_status_display }}</td>
    {% endfor %}

    <ul class="pagination">
        {{page_string}}
    </ul>

"""
from django.utils.safestring import mark_safe


class Pagination(object):

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        """
        :param request: 請求的對象
        :param queryset:  符合條件的數據(根據這個數據給他進行分頁處理)
        :param page_size: 每頁顯示多少條數據
        :param page_param: 在URL中傳遞的獲取分頁的參數 例如: /pretty/list/?page=12
        :param plus: 顯示當前頁的 前或後幾頁(頁碼)
        """
        from django.http.request import QueryDict
        import copy
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        # query_dict.setlist('xx', [11])

        self.page_param = page_param
        page = request.GET.get(page_param, "1")  # 獲取當前頁

        self.page_size = page_size

        total_count = queryset.count()
        total_page, page_other = divmod(total_count, page_size)  # 取得總頁碼數。取整數(商數)->總頁碼數、餘數->多出的數據也成一頁
        if page_other:  # 如果餘數有數值為True也就是無法滿足page_size為完整一頁時，但數據也是要呈現出來
            total_page += 1
        self.total_page_count = total_page

        # --------頁碼搜尋不超過目前最大頁碼---------

        if page.isdecimal():  # 判斷字串是否只有十進製的數字
            page = int(page)  # 確定只有字串中只有數字才進行數據類型轉換成整型
            if page > self.total_page_count:
                page = self.total_page_count
        else:
            page = 1  # 字串中不是只有數字則默認等於1
        self.page = page
        # print(self.page)

        self.start = max(0, (page - 1) * page_size)  # 才會符合切片從0開始計算
        self.end = max(0, page * page_size)

        self.page_queryset = queryset[self.start:self.end]

        self.plus = plus  # 決定當前位置的前後各出現幾頁

    def html(self):
        # 數據庫中的數據比較少，都沒有達到11頁
        if self.total_page_count <= self.plus * 2 + 1:  # 11 ，如果之後網頁呈現頁碼數量要改的話，不用手動改此，改plus即可
            start_page = 1
            end_page = self.total_page_count

        # 8.2 數據庫中數據大於11頁
        else:
            # 8.3 當前頁<5
            if self.page <= self.plus:  # 判斷當前頁碼
                start_page = 1
                end_page = self.plus * 2 + 1

            # 8.4 當前頁+5 >總頁碼
            else:
                start_page = self.page - self.plus
                if (self.page + self.plus) > self.total_page_count:  # 判斷頁碼是否超出數據
                    end_page = self.total_page_count
                else:
                    end_page = self.page + self.plus

        page_str_list = []
        n = "\n"
        self.query_dict.setlist(self.page_param, [1])  # "page": 1
        self.query_dict.urlencode()  # page=1

        # 10. 頁碼首頁
        home_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">首頁</a></li>'
        page_str_list.append(home_page)

        # 9. 上一頁
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            prev_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">上一頁</a></li>'
        else:
            self.query_dict.setlist(self.page_param, [1])
            prev_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">上一頁</a></li>'
        page_str_list.append(prev_page)

        # 5. 生成頁碼，做成列表且去除換行
        for i in range(start_page, end_page + 1):  # range是前取後不取因此記得要在原本數值上+1
            self.query_dict.setlist(self.page_param, [i])
            # 實現當前選取頁面 html裡面加上 active
            if i == self.page:
                page_list = f'<li class="page-item active" aria-current="page"><a class="page-link" href="?{self.query_dict.urlencode()}">{i}</a></li>'
            else:
                page_list = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">{i}</a></li>'
            page_str_list.append(page_list)

        # 9.1 下一頁
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            next_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">下一頁</a></li>'
        else:
            self.query_dict.setlist(self.page_param, [self.total_page_count])
            next_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">下一頁</a></li>'
        page_str_list.append(next_page)

        page_string = mark_safe(f'{"".join(page_str_list)}{n}')

        return page_string








