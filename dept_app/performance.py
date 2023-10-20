import time

import logging

logger = logging.getLogger(__name__)


# 定義一個名為performance_logger_middleware的中間件函數，
# 這個函數接收一個名為get_response的參數，
# get_response是一個函數，當調用它並傳入一個請求對象時，Django會處理該請求並返回一個響應對象。
def performance_logger_middleware(get_response):
    # 定義一個名為middleware的內部函數，
    # 這個函數接收一個名為request的參數，代表一個HTTP請求。
    def middleware(request):
        # 健康檢查的訪問 http://localhost:8001，訪問成功不輸出為日誌
        if "8001" in request.get_host():
            response = get_response(request)
            return response

        # 獲取當前時間，並將它存儲到start_time變數中
        start_time = time.time()

        # 調用get_response函數，傳入請求對象，並將返回的響應對象存儲到response變數中
        response = get_response(request)

        # 獲取當前時間，並減去start_time，得到處理請求的時間，然後將它存儲到duration變數中
        duration = time.time() - start_time

        # 將處理時間（以毫秒為單位）添加到響應對象的X-Page-Duration-ms頭部
        response["X-Page-Duration-ms"] = int(duration * 1000)

        # 將一條包含處理時間、請求路徑和請求的GET參數的訊息添加到日誌中
        logger.info("[performance] %s %s %s",
                    duration,
                    request.path,
                    request.GET.dict()
                    )

        # 返回響應對象
        return response

    # 返回middleware函數
    return middleware
