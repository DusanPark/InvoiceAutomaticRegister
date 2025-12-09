"""
SQL Server 데이터베이스에 table_prompt 컬럼 추가 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invoice_system.settings')
django.setup()

import pyodbc
from core.models import Service

def add_table_prompt_column():
    """모든 서비스 데이터베이스에 table_prompt 컬럼 추가"""

    services = Service.objects.filter(is_active=True)

    for service in services:
        if not all([service.db_host, service.db_name, service.db_user, service.db_password]):
            print(f"[SKIP] {service.name}: DB 정보 불완전")
            continue

        try:
            # 연결 문자열 구성
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={service.db_host},{service.db_port or '1433'};"
                f"DATABASE={service.db_name};"
                f"UID={service.db_user};"
                f"PWD={service.db_password};"
                "TrustServerCertificate=yes;"
            )

            print(f"\n[{service.name}] 연결 중...")
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()

            # 컬럼이 이미 존재하는지 확인
            check_sql = """
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'table_process_configs'
            AND COLUMN_NAME = 'table_prompt'
            """
            cursor.execute(check_sql)
            exists = cursor.fetchone()[0]

            if exists:
                print(f"[{service.name}] table_prompt 컬럼이 이미 존재합니다.")
            else:
                # 컬럼 추가
                add_column_sql = """
                ALTER TABLE table_process_configs
                ADD table_prompt NVARCHAR(MAX) NULL;
                """
                cursor.execute(add_column_sql)
                conn.commit()
                print(f"[{service.name}] table_prompt 컬럼 추가 완료!")

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"[{service.name}] 오류 발생: {str(e)}")
            continue

    print("\n완료!")

if __name__ == "__main__":
    add_table_prompt_column()
