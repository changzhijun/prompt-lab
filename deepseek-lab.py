# -*- coding: utf-8 -*-
'''
Created on 2025年2月20日
@author: changzhijun
'''

import json
import traceback
import time
import requests
from flask import Flask, request, jsonify ,send_file
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求
# 自定义 JSON 编码器，确保中文不被转义
app.json.ensure_ascii = False


@app.route('/api/chat', methods=['POST'])
def chat():
    try:

        # 检查是否有文件在请求中
        if 'input' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        else:
            file_input = request.files['input']
        try:
            # 读取文件内容
            input_content = file_input.read().decode('utf-8')  # 假设文件是UTF-8编码的txt文件
            print('\n****************************************************************************')
            print(f'>>> [1/4] input: {input_content}\n')

        except Exception as e:
            return jsonify({"error": f"Failed to read input file: {str(e)}"}), 500

        if 'prompt' not in request.files:
            prompt_content = None
        else:
            file_prompt = request.files['prompt']
            try:
                # 读取文件内容
                prompt_content = file_prompt.read().decode('utf-8')  # 假设文件是UTF-8编码的txt文件
                #print('----------------------------------------------------------------------------')
                print(f'>>> [2/4] prompt: {prompt_content}\n')

            except Exception as e:
                return jsonify({"error": f"Failed to read input file: {str(e)}"}), 500

        ## 编辑提示工程
        prompt_engineering = design_prompt_engineering(input_content, prompt_content)
        print(f'>>> [3/4] prompt_engineering={json.dumps(prompt_engineering, indent=4, ensure_ascii=False)}')

        ## 调用大模型
        response = call_deepseek(prompt_engineering)
        #print('----------------------------------------------------------------------------')
        print(f'>>> [4/4] response={response}\n\n')

        ## 返回
        return response

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


## 提示工程
def design_prompt_engineering(input, prompt):
    '''
    编辑提示工程
    :param question:
    :param data_list:
    :return:
    '''

    prompt_engineering = {
        #"model": "deepseek-r1:1.5b",   
        "model": "deepseek-32b",
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": input
            }
        ],
        "stream": False ,
        "temperature": 0,
        "max_tokens": 10000
    }

    #print('----------------------------------------------------------------------------')


    ## 返回
    return prompt_engineering

def call_deepseek(prompt_engineering):
    ## 调用大模型
    headers = {
        "Content-Type": "application/json",
    }
    
    url = 'http://127.0.0.1:11434/api/chat'             # 本地、ollama 模型、直接IP访问
    url = 'http://10.3.11.78:9091/v1/chat/completions'  # 内网、vllm模型、直接IP访问
    url = 'https://deepseek.las.ac.cn/qingbao2/v1/chat/completions' # 外网、vllm模型、域名访问
    
    # 发送GET请求，并设置stream=True以启用流式处理
    print('----------------------------------------------------------------------------')
    print(f'>>> calling the deepseek ...')
    # 记录开始时间
    start_time = time.time()
    response = requests.post(url, headers=headers, json=prompt_engineering, stream=False)
    end_time = time.time()
    print(f'    elapse time: {(end_time - start_time):.3f} seconds')
    response.json()['elapse'] = f"{(end_time - start_time):.3f} seconds"

    reponse_string = json.dumps(response.json(), ensure_ascii=False, indent=4)
    #print(reponse_string)

    # 返回
    return reponse_string



if __name__ == '__main__':

    app.config['JSON_AS_ASCII'] = False  # 解决中文乱码问题
    app.run(host='0.0.0.0', port='8001', debug=False)
