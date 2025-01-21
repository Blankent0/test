from flask import Flask, request, make_response
import xml.etree.ElementTree as ET
import time

app = Flask(__name__)

# 用于存储用户的数字输入历史
user_numbers = {}

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    # 微信服务器进行URL验证时使用GET请求
    if request.method == 'GET':
        # 获取参数
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')
        return echostr

    # 处理微信服务器发来的消息
    if request.method == 'POST':
        xml_data = request.data
        root = ET.fromstring(xml_data)
        
        # 获取基本信息
        msg_type = root.find('MsgType').text
        from_user = root.find('FromUserName').text
        to_user = root.find('ToUserName').text
        
        # 如果是文本消息
        if msg_type == 'text':
            content = root.find('Content').text
            try:
                # 尝试将输入转换为数字
                number = float(content)
                
                # 获取该用户的数字历史，如果没有则创建新列表
                if from_user not in user_numbers:
                    user_numbers[from_user] = []
                
                # 添加新数字到列表
                user_numbers[from_user].append(number)
                
                # 计算总和
                total = sum(user_numbers[from_user])
                
                # 准备回复消息
                reply = f"已收到数字：{number}\n当前所有数字的和为：{total}"
                
            except ValueError:
                reply = "请输入一个有效的数字！"
            
            # 构建返回的XML
            xml_reply = f"""
            <xml>
            <ToUserName><![CDATA[{from_user}]]></ToUserName>
            <FromUserName><![CDATA[{to_user}]]></FromUserName>
            <CreateTime>{int(time.time())}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{reply}]]></Content>
            </xml>
            """
            
            response = make_response(xml_reply)
            response.content_type = 'application/xml'
            return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)