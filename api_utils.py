import requests
from openai import OpenAI
from config import API_KEY, API_URL
def extract_criteria_from_text(text):
    """调用 AI API 提取入排标准"""
    try:
        client = OpenAI(api_key=API_KEY, base_url=API_URL)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "you are a helpful assistant"},
                {"role": "user", "content": f"请从以下文本中具体的和严谨的提取方案中Inclusion Criteria和Exclusion Criteria两部分原文，不要加入任何新内容：\n{text}"}
            ]
        )
        
        # 直接从response中获取内容
        message_content = response.choices[0].message.content
        return True, message_content

    except requests.exceptions.Timeout:
        return False, "连接超时，请检查网络连接"
    except requests.exceptions.ConnectionError:
        return False, "无法连接到服务器，请检查网络连接"
    except Exception as e:
        return False, f"发生错误：{str(e)}"

def analyze_patient_criteria(criteria, patient_case):
    """使用 deepseek-reasoner 分析患者是否符合入排标准"""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        full_api_url = f"{API_URL}/v1/chat/completions"  # 确保URL是完整的
        
        # 限制文本长度，防止token超限
        max_criteria_length = 10000  # 可根据实际情况调整
        max_case_length = 20000
        
        criteria_length = len(criteria)
        case_length = len(patient_case)
        
        criteria_truncated = False
        case_truncated = False
        
        if criteria_length > max_criteria_length:
            criteria = criteria[:max_criteria_length] + f"...[内容过长已截断，原长度: {criteria_length} 字符]"
            criteria_truncated = True
            print(f"入排标准内容过长，已截断至{max_criteria_length}字符，原长度: {criteria_length}字符")
            
        if case_length > max_case_length:
            patient_case = patient_case[:max_case_length] + f"...[内容过长已截断，原长度: {case_length} 字符]"
            case_truncated = True
            print(f"患者病例内容过长，已截断至{max_case_length}字符，原长度: {case_length}字符")
        
        # 在界面上显示长度信息的提示
        length_info = ""
        if criteria_truncated:
            length_info += f"入排标准内容长度: {criteria_length}字符，超过{max_criteria_length}字符限制，已截断。\n"
        if case_truncated:
            length_info += f"患者病例内容长度: {case_length}字符，超过{max_case_length}字符限制，已截断。\n"
        
        if length_info:
            length_info += "内容过长可能影响分析结果的准确性。\n\n"
        
        payload = {
            "model": "deepseek-chat",  # 尝试使用不同的模型
            "messages": [{
                "role": "user", 
                "content": f"""请分析以下患者病例是否符合入排标准，并在病例中标注符合和不符合的条目：
                
入排标准：
{criteria}

患者病例：
{patient_case}

请按以下格式输出：
1. 符合的条目：(在原文中标注并解释)
2. 不符合的条目：(在原文中标注并解释)
3. 总体结论：
"""
            }],
            "temperature": 0.7,
            "max_tokens": 5000
        }
        
        print(f"正在发送请求到: {full_api_url}")
        
        response = requests.post(full_api_url, headers=headers, json=payload, timeout=120)
        
        # 打印详细的响应信息
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code != 200:
            return f"{length_info}分析失败：API响应状态码 {response.status_code} - {response.text}"
        
        response_json = response.json()
        
        # 解析响应内容
        if "choices" in response_json and len(response_json["choices"]) > 0:
            content = response_json["choices"][0].get("message", {}).get("content", "")
            if content:
                return f"{length_info}{content}"
        
        return f"{length_info}分析失败：无法解析API响应 - {response_json}"
            
    except requests.exceptions.Timeout:
        return "分析失败：请求超时，请检查网络连接或稍后重试"
    except requests.exceptions.ConnectionError:
        return "分析失败：网络连接错误，无法连接到服务器"
    except Exception as e:
        return f"分析失败：未知错误 - {str(e)}"

def organize_patient_case(case_text):
    """使用AI模型整理患者病例"""
    try:
        client = OpenAI(api_key=API_KEY, base_url=API_URL)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "you are a helpful assistant"},
                {"role": "user", "content": f"将文本整理成患者病例，至少包含四部分分别是：血液生化指标/尿检/凝血检查/血常规，如有其他涉及到临床研究入排的信息，单独列举出来。\n\n{case_text}"}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # 获取响应内容
        message_content = response.choices[0].message.content
        return True, message_content

    except requests.exceptions.Timeout:
        return False, "连接超时，请检查网络连接"
    except requests.exceptions.ConnectionError:
        return False, "无法连接到服务器，请检查网络连接"
    except Exception as e:
        return False, f"发生错误：{str(e)}"