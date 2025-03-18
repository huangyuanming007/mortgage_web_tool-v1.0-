import streamlit as st
import numpy as np
import numpy_financial as npf

def calculate_mortgage_savings(
    initial_principal: float,
    monthly_payment: float,
    annual_rate: float,
    prepayment_amount: float,
    prepayment_freq: str,
    verbose: bool
) -> dict:
    """
    计算等额本息房贷在提前还本方案下的总利息和还款期限
    """
    monthly_rate = annual_rate / 12 / 100  # 月利率（小数形式）
    current_principal = initial_principal
    total_interest = 0.0
    month_count = 0
    prepayment_month = 0  # 记录每年提前还款的月份（如3月为第3个月）
    history = []  # 记录每月剩余本金和利息

    # 原计划（无提前还款）总利息计算
    original_total_interest = (monthly_payment * npf.nper(monthly_rate, -monthly_payment, initial_principal)) - initial_principal

    while current_principal > 0:
        month_count += 1
        # 计算当月利息和本金
        monthly_interest = current_principal * monthly_rate
        monthly_principal = monthly_payment - monthly_interest
        total_interest += monthly_interest

        # 更新剩余本金
        current_principal = current_principal - monthly_principal

        # 处理提前还款
        if prepayment_freq == 'monthly':
            # 每月提前还款
            current_principal -= prepayment_amount
        elif prepayment_freq == 'yearly':
            # 每年固定月份提前还款（例如3月）
            if (month_count - prepayment_month) % 12 == 0:
                current_principal -= prepayment_amount
                prepayment_month = month_count

        # 防止剩余本金为负
        current_principal = max(current_principal, 0)

        # 记录历史数据
        history.append({
            "month": month_count,
            "remaining_principal": current_principal,
            "monthly_interest": monthly_interest
        })

        if verbose:
            st.write(f"第{month_count}个月 | 剩余本金: {current_principal:.2f}元 | 当月利息: {monthly_interest:.2f}元")

    interest_saved = original_total_interest - total_interest

    return {
        'total_months': month_count,
        'total_interest': total_interest,
        'interest_saved': interest_saved,
        'history': history
    }

def main():
    st.title("房贷提前还款计算器 🏠")
    st.markdown("通过输入参数，计算不同提前还款策略下的利息节省和还款时间。")

    # 输入参数表单
    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            initial_principal = st.number_input(
                "初始剩余本金（元）",
                min_value=0.0,
                value=1124778.57,
                help="例如：2025年3月提前还款后的本金"
            )
            monthly_payment = st.number_input(
                "月供（元）",
                min_value=0.0,
                value=6251.26,
                help="调整利率后的月供金额"
            )
            annual_rate = st.number_input(
                "年利率（%）",
                min_value=0.0,
                value=3.3,
                help="例如：3.3 表示3.3%%"
            )
        with col2:
            prepayment_amount = st.number_input(
                "每次提前还款金额（元）",
                min_value=0.0,
                value=1000.0,
                help="每月或每年额外还款的金额"
            )
            prepayment_freq = st.selectbox(
                "提前还款频率",
                options=["monthly", "yearly"],
                format_func=lambda x: "每月" if x == "monthly" else "每年",
                help="选择每月或每年还款"
            )
            verbose = st.checkbox("显示每月明细")

        submitted = st.form_submit_button("开始计算")

    if submitted:
        # 执行计算
        result = calculate_mortgage_savings(
            initial_principal=initial_principal,
            monthly_payment=monthly_payment,
            annual_rate=annual_rate,
            prepayment_amount=prepayment_amount,
            prepayment_freq=prepayment_freq,
            verbose=verbose
        )

        # 展示结果
        st.subheader("计算结果 📊")
        st.markdown(f"**总还款月数**: {result['total_months']}个月（约{result['total_months'] // 12}年{result['total_months'] % 12}个月）")
        st.markdown(f"**总利息支出**: {result['total_interest']:.2f}元")
        st.markdown(f"**节省利息**: {result['interest_saved']:.2f}元")

        # 导入 pandas
        import pandas as pd

        # 绘制剩余本金变化图表
        st.subheader("剩余本金变化趋势 📉")
        history = result['history']
        # 将数据转换为 DataFrame，并指定列名
        df = pd.DataFrame({
            "月份": [x['month'] for x in history],
            "剩余本金（元）": [x['remaining_principal'] for x in history]
        })
        # 使用 DataFrame 和列名绘制图表
        st.line_chart(
            data=df,
            x="月份",  # 指定 x 轴列名
            y="剩余本金（元）",  # 指定 y 轴列名
            use_container_width=True
        )

if __name__ == "__main__":
    main()