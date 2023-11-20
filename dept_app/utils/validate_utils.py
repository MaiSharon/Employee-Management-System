import inspect
import re
import logging

logger = logging.getLogger(__name__)

def validate_search(search_input):
    """
    驗證用戶輸入的搜尋字符串，並記錄相關的日誌信息。

    Main features:
    - 檢查輸入長度不可超過20個字符。
    - 只允許包含大小寫字母、數字、下劃線和點。
    - 日誌: 記錄調用此函數的文件和行號
    - 日誌: 記錄輸入字符串包含驗證未通過與通過的。

    Args:
        search_input (str): 接收用戶輸入的字符串。

    Returns:
        str: 當輸入通過驗證->返回原始輸入字符串；否->返回空字符串。

    """
    if search_input:
        # 記錄調用此函數的文件和行號
        caller_frame = inspect.stack()[1]
        filename = caller_frame.filename.split("\\")[-1]  # 取得文件名，不包括路徑
        lineno = caller_frame.lineno  # 取得行號
        file_info = f"[file_info:{filename}:{lineno}]"

        # 驗證字符串不可超過20個
        if len(search_input) > 20:
            logger.warning(f'{file_info}- Input too long: "{search_input}"')
            return ''
        # 驗證字符串只允許大小寫字母、數字、下畫線'_'和點'.'
        elif not re.match("^[a-zA-Z0-9_.]+$", search_input):
            logger.warning(f'{file_info}- Invalid text: "{search_input}"')
            return ''
        # 驗證通過
        else:
            logger.info(f'{file_info}- Search: "{search_input}"')
            return search_input
    else:
        return ''