from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class AuthMiddleware(MiddlewareMixin):
    """登入校驗"""

    def process_request(self, request):

        # 如果沒有返回值(返回None)，繼續往後走
        # 如果有返回值 HttpResponse, render, redirect，則直接在此中間件中斷不繼續向後執行

        # 0.排除不需要登入即可到訪的頁面
        if request.path_info in ["/login/","/user/list/", "/image/code/", "/callback/"]:
            return
        # 1.(未登入時會有死循環，需要做排除)讀取當前session訊息，若有才能進入，若沒有則返回
        info_dic = request.session.get("info")
        if info_dic:
            print("M1, Coming")
            return
        # 2.若沒有則返回登入夜面
        else:
            print("M1, Out")
            return redirect("/login/")


    # def process_response(self, request, response):
    #     print("M1, Outing")
    #
    #     return response






