"""
财务工具箱 - 增强功能模块
包含数据导出、备份、高级分析等功能
"""
import streamlit as st

# ========== 性能优化 ==========
# Session State: 保存用户输入
if '_session_init' not in st.session_state:
    st.session_state._session_init = True

import pandas as pd
from datetime import datetime
from utils.database import get_connection, export_to_excel, get_dashboard_stats
from utils.formatters import format_currency

st.set_page_config(page_title="增强功能", page_icon="🚀", layout="wide")

st.title("🚀 增强功能")

tab1, tab2, tab3, tab4 = st.tabs(["数据导出", "数据导入", "备份恢复", "高级分析"])

with tab1:
    st.subheader("导出数据到 Excel")
    
    tables = {
        'invoice': '发票数据',
        'bank_statement': '银行流水',
        'company_statement': '企业账务',
        'voucher': '凭证主表',
        'voucher_entry': '凭证分录',
        'ar_ap': '应收应付',
        'calendar_event': '日历事件',
        'financial_metrics': '财务指标',
    }
    
    selected_table = st.selectbox("选择要导出的表", list(tables.keys()), format_func=lambda x: tables[x])
    
    if st.button("导出 Excel", type="primary"):
        try:
            conn = get_connection()
            df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
            conn.close()
            
            if not df.empty:
                # 创建 Excel 下载
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name=selected_table)
                
                st.download_button(
                    label=f"📥 下载 {tables[selected_table]}.xlsx",
                    data=output.getvalue(),
                    file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success(f"导出成功，共 {len(df)} 条记录")
            else:
                st.warning("该表暂无数据")
        except Exception as e:
            st.error(f"导出失败：{e}")

with tab2:
    st.subheader("从 Excel 导入数据")
    
    uploaded_file = st.file_uploader("上传 Excel 文件", type=['xlsx', 'xls'])
    target_table = st.selectbox("导入到表", list(tables.keys()), format_func=lambda x: tables[x])
    
    if uploaded_file and st.button("开始导入"):
        try:
            df = pd.read_excel(uploaded_file)
            st.write(f"预览数据（前 5 行）:")
            st.dataframe(df.head())
            
            conn = get_connection()
            count = 0
            errors = 0
            
            for _, row in df.iterrows():
                try:
                    row_dict = row.dropna().to_dict()
                    if not row_dict:
                        continue
                    
                    columns = ', '.join(row_dict.keys())
                    placeholders = ', '.join(['?' for _ in row_dict])
                    
                    # 检查是否有唯一键冲突
                    cursor = conn.cursor()
                    values = list(row_dict.values())
                    
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {target_table} ({columns}) VALUES ({placeholders})",
                        values
                    )
                    count += 1
                except Exception as e:
                    errors += 1
                    continue
            
            conn.commit()
            conn.close()
            
            st.success(f"导入完成：成功 {count} 条，失败 {errors} 条")
            
        except Exception as e:
            st.error(f"导入失败：{e}")

with tab3:
    st.subheader("数据备份与恢复")
    
    st.warning("⚠️ 备份操作会导出所有数据，恢复操作会清空现有数据并导入备份文件")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 备份全部数据")
        if st.button("备份所有数据", type="primary"):
            try:
                conn = get_connection()
                backup_data = {}
                
                for table_name in tables.keys():
                    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
                    backup_data[table_name] = df.to_dict('records')
                
                conn.close()
                
                import json
                backup_json = json.dumps(backup_data, ensure_ascii=False, default=str)
                
                st.download_button(
                    label="📥 下载备份文件",
                    data=backup_json,
                    file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.success("备份数据已生成")
                
            except Exception as e:
                st.error(f"备份失败：{e}")
    
    with col2:
        st.markdown("### 📥 恢复数据")
        backup_file = st.file_uploader("上传备份文件", type=['json'], key="restore")
        
        if backup_file and st.button("恢复数据", type="primary"):
            try:
                import json
                backup_data = json.load(backup_file)
                
                conn = get_connection()
                cursor = conn.cursor()
                
                total_imported = 0
                for table_name, records in backup_data.items():
                    for record in records:
                        try:
                            columns = ', '.join(record.keys())
                            placeholders = ', '.join(['?' for _ in record])
                            cursor.execute(
                                f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})",
                                list(record.values())
                            )
                            total_imported += 1
                        except:
                            pass
                
                conn.commit()
                conn.close()
                
                st.success(f"恢复完成，共导入 {total_imported} 条记录")
                st.rerun()
                
            except Exception as e:
                st.error(f"恢复失败：{e}")

with tab4:
    st.subheader("高级数据分析")
    
    # 仪表盘统计
    stats = get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("发票总数", stats['invoice_count'])
    col2.metric("发票总额", format_currency(stats['invoice_total']))
    col3.metric("应收账款", format_currency(stats['ar_total']))
    col4.metric("应付账款", format_currency(stats['ap_total']))
    
    st.divider()
    
    # 月度趋势分析
    st.markdown("### 📈 月度趋势分析")
    
    conn = get_connection()
    
    # 发票月度统计
    df_invoice = pd.read_sql_query("""
        SELECT strftime('%Y-%m', date) as month, 
               COUNT(*) as count, 
               SUM(amount) as total
        FROM invoice 
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """, conn)
    
    if not df_invoice.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 发票数量趋势")
            import plotly.express as px
            fig = px.line(df_invoice, x='month', y='count', markers=True, title='月度发票数量')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 发票金额趋势")
            fig = px.bar(df_invoice, x='month', y='total', title='月度发票金额')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无发票数据")
    
    conn.close()
