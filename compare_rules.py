from typing import List
import requests
from jsonpath import jsonpath


class get_rules:
    def __init__(self, url, cookies):
        self.url = url
        self.cookies = {'JSESSIONID': cookies, "rememberMe": "false"}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.33",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"}
        self.json = {
            "cccCompanyCode": "01",
            "taskType": "01",
            "validFlag": "1",
            "currentCompanyGroup": {
                "cccCompanyCode": "01",
                "companyFullName": "中国人寿财产保险股份有限公司",
                "companyName": "中国人寿财产保险股份有限公司",
                "tenementId": "CLCC",
                "$$hashKey": "object:104"
            },
            "currentCompany": {
                "cccCompanyCode": "01",
                "companyCode": "00000000",
                "companyFullName": "中国人寿财产保险股份有限公司",
                "companyName": "中国人寿财产保险股份有限公司",
                "type": "Company"
            },
            "page": 1,
            "pageSize": 300
        }

    def get_rules(self):
        """
        获取ruleNo,ruleSpecId
        :return:
        """
        url = self.url + "/rule/mgmt/fetchRuleQueryResult"
        response = requests.post(url, headers=self.headers, cookies=self.cookies, json=self.json)
        rules = str(jsonpath(response.json(), expr='$..ruleNo'))
        ruleSpecId = str(jsonpath(response.json(), expr='$..ruleSpecId'))
        return rules, ruleSpecId

    def get_single_rule(self, ruleSpecId):
        paramSpecId = dict()
        url = self.url + "/rule/mgmt/loadBySpecId/{}/01".format(ruleSpecId)
        response = requests.post(url, headers=self.headers, cookies=self.cookies, json=self.json)
        for i in range(len(jsonpath(response.json(), expr='$..ruleParamRowList'))):
            paramSpecId_name = str(jsonpath(response.json(), expr='$..paramSpecId')[i])
            paramSpecId_value = str(jsonpath(response.json(), expr='$..value')[i])
            paramSpecId[paramSpecId_name] = [paramSpecId_value]
        return paramSpecId


def main(urls: List, cookies: List):
    rules = list()
    ruleSpecIds = list()
    if len(urls) != len(cookies):
        raise "请保持链接跟cookies一一对应"
    else:
        # 获取两个环境中的以应用规则
        for i in range(len(urls)):
            results = get_rules(urls[i], cookies[i]).get_rules()
            rule = results[0].strip("[").strip("]").replace("'", "").replace(" ", "").split(",")
            ruleSpecId = results[1].strip("[").strip("]").replace("'", "").replace(" ", "").split(",")
            rules.insert(i, rule)
            ruleSpecIds.insert(i, ruleSpecId)

    if len(rules[0]) == len(rules[1]):
        print("两个环境规则数量一致,都是{}".format(len(rules[0])))

    # 获取初始化环境，和其他环境中，不一样的规则 →  只获取初始化环境有，而其他环境没有的
    diff_rules = dict()
    diff_rules[urls[0]] = set(rules[0]) - set(rules[1])

    # 获取参数配置不一样的规则
    diff_params = list()
    for i in range(len(rules[0])):
        ruleSpecId = ruleSpecIds[0][i]
        params_main = get_rules(urls[0], cookies[0]).get_single_rule(ruleSpecId)
        params_rel = get_rules(urls[1], cookies[1]).get_single_rule(ruleSpecId)
        for param in params_main.keys():
            if params_main[param] != params_rel[param]:
                diff_params.append(rules[0][i])

    return diff_rules, diff_params


if __name__ == "__main__":
    # 第一个链接为初始化环境
    url = ["http://192.168.200.104:8080/apd-web", "http://9.23.27.193:7001/web-suite"]
    cookies = ["88D411E1C8886AB787938DB2E8FA9018",
               "97FE36MSA_E9_80A6FbJbzfSTukJE9Hlp6IDM7rrS-WqOp9I8a0U!-1580813997"]
    print(main(url, cookies))