import os

import pandas as pd

file_path = os.getcwd()


def get_excel_rules():
    file_name = "【2.4.1版本】规则组件【国寿升级版本】.xlsx"
    # 打开excel中名为“规则集”的sheet，且跳过第一行
    # dtype=str  以字符串读入，否则规则编号，会变成数字
    datas = pd.read_excel(file_path + "\\" + file_name, sheet_name="规则集", skiprows=1, dtype=str)

    # 行数
    # nrows = datas.shape[0]
    # 列数
    # nclos = datas.columns.size

    datas = datas[datas["国寿V2.4.1使用情况"] == "使用"]
    datas = datas.get(["新规则编号", "项目参数"])

    # 筛选数据后，需要重新设置行号（序列号）
    datas = datas.reset_index(drop=True)

    rules = dict()
    param_spec = dict()
    for i in range(len(datas)):
        params = datas.loc[i, "项目参数"]
        if params is None or params == "/":
            params = None
        else:
            params = params.split("\n")
            for param in params:
                if "/" in param:
                    param = param.split("/")

    return params



if __name__ == "__main__":
    print(get_excel_rules())
