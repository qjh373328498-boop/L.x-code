"""
📁 财报模板下载
"""
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="模板下载", page_icon="📁", layout="wide")

st.title("📁 财报模板下载")

st.markdown("""
### 使用说明

为了获得最佳的解析效果，请使用以下模板格式上传财报数据。

下载 Excel 模板后，只需填写对应数据即可。
""")

# 创建模板文件
def create_template():
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # 资产负债表
        balance_data = pd.DataFrame({
            '项目': ['货币资金', '应收账款', '存货', '流动资产合计', '固定资产', '资产总计', 
                    '流动负债合计', '负债合计', '所有者权益合计'],
            '期末余额': [0.0] * 9,
            '期初余额': [0.0] * 9
        })
        balance_data.to_excel(writer, sheet_name='资产负债表', index=False)
        
        # 利润表
        income_data = pd.DataFrame({
            '项目': ['营业总收入', '营业收入', '营业成本', '毛利', '营业利润', '净利润'],
            '本期金额': [0.0] * 6,
            '上期金额': [0.0] * 6
        })
        income_data.to_excel(writer, sheet_name='利润表', index=False)
        
        # 现金流量表
        cash_data = pd.DataFrame({
            '项目': ['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', 
                    '筹资活动产生的现金流量净额'],
            '本期金额': [0.0] * 3,
            '上期金额': [0.0] * 3
        })
        cash_data.to_excel(writer, sheet_name='现金流量表', index=False)
    
    return buffer.getvalue()

# 提供下载
st.download_button(
    label="📥 下载 Excel 模板",
    data=create_template(),
    file_name="财报模板.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary"
)

st.markdown("""
### 填写说明

**资产负债表**：
- 填写「期末余额」列
- 关键项目：货币资金、应收账款、存货、流动资产合计、固定资产、资产总计、流动负债合计、负债合计、所有者权益合计

**利润表**：
- 填写「本期金额」列
- 关键项目：营业收入、营业成本、毛利、营业利润、净利润

**现金流量表**：
- 填写「本期金额」列
- 关键项目：经营活动现金流净额、投资活动现金流净额、筹资活动现金流净额

### 快速录入

如果数据较少，也可以直接在 Excel 中创建以下格式：

```
| 项目名称 | 金额 |
|---------|------|
| 营业收入 | 1000000 |
| 净利润 | 150000 |
| ... | ... |
```

系统会自动识别常见财务项目名称。
""")
