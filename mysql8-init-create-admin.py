# mysql8-init-create-admin.py
import os
import django
from django.contrib.auth.hashers import make_password

# 設置Django的設置模塊。這是Django項目的配置入口點。
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prj_dept.settings')

# 初始化Django環境。這一步讓腳本能夠使用Django的模型和其他功能。
django.setup()

# 確保在使用 Admin 模型之前，所有應用程序都已加載。
from dept_app.models import Admin

# 從環境變量中獲取管理員的用戶名和密碼。如果環境變量未設置，則使用默認值。
username = os.getenv('MYSQL8_ADMIN_USERNAME', 'b')
password = os.getenv('MYSQL8_ADMIN_PASSWORD', 'b')

# 對密碼進行哈希處理，以便以安全的方式存儲在數據庫中。
hashed_password = make_password(password)

# 檢查管理員用戶是否已經存在。如果不存在，則創建新的管理員用戶。
if not Admin.objects.filter(username=username).exists():
    Admin.objects.create(username=username, password=hashed_password)
    print(f"Admin user {username} created successfully.")
else:
    print(f"Admin user {username} already exists.")

print(f"Hashed password for {username}: {hashed_password}")
