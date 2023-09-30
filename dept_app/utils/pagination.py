from django.utils.safestring import mark_safe

class Pagination(object):

    def __init__(self, request, queryset, page_size=5, page_param="page", plus=5):
        """
        初始化分頁對象。

        Args:
            request: HttpRequest對象，網絡請求對象。
            queryset: QuerySet，要分頁的查詢集。
            page_size: int, 可選，每頁包含的項目數。
            page_param: str, 可選，查詢字符串中頁面參數的名稱。
            plus: int, 可選，當前頁面前後要顯示的頁數。
        """
        from django.http.request import QueryDict
        import copy

        # 深度複製請求參數並使其可變
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict
        self.page_param = page_param
        self.page_size = page_size

        # 獲取當前頁數，默認為第一頁
        page = request.GET.get(page_param, "1")

        # 計算總頁數
        total_count = queryset.count()
        total_page, remainder = divmod(total_count, page_size)
        if remainder:
            total_page += 1
        self.total_page_count = total_page

        # 確保當前頁數在有效範圍內
        if page.isdecimal():
            page = int(page)
            if page > self.total_page_count:
                page = self.total_page_count
        else:
            page = 1
        self.page = page

        # 計算當前頁的資料範圍
        self.start = max(0, (page - 1) * page_size)
        self.end = self.start + page_size

        # 取出當前頁的數據
        self.page_queryset = queryset[self.start:self.end]

        # 設置顯示的頁碼範圍
        self.plus = plus

    def generate_html(self):
        """
        生成 HTML 分頁控制元件。

        Returns:
            str: HTML 分頁控件
        """
        page_str_list = []

        # 處理「上一頁」
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
        else:
            self.query_dict.setlist(self.page_param, [1])
        prev_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">Previous</a></li>'
        page_str_list.append(prev_page)

        # 計算要顯示的頁碼範圍
        if self.total_page_count <= self.plus * 2 + 1:
            start_page, end_page = 1, self.total_page_count
        else:
            if self.page <= self.plus:
                start_page, end_page = 1, self.plus * 2 + 1
            else:
                start_page = self.page - self.plus
                end_page = min(self.total_page_count, self.page + self.plus)

        # 生成頁碼列表
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                page_str_list.append(f'<li class="page-item active" aria-current="page"><a class="page-link" href="?{self.query_dict.urlencode()}">{i}</a></li>')
            else:
                page_str_list.append(f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">{i}</a></li>')

        # 處理「下一頁」
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
        else:
            self.query_dict.setlist(self.page_param, [self.total_page_count])
        next_page = f'<li class="page-item"><a class="page-link" href="?{self.query_dict.urlencode()}">Next</a></li>'
        page_str_list.append(next_page)

        # 返回生成的HTML
        return mark_safe(''.join(page_str_list))
