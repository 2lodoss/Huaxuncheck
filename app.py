import io
import json
import logging
import os
import platform
import subprocess
import threading
import time
import zipfile
from datetime import datetime
import pytz

import netmiko
import pandas as pd
from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import send_from_directory

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network_inspection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 设置时区
tz = pytz.timezone('Asia/Shanghai')

# 设备模型
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    enable_password = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(100), nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    commands = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='unknown')
    last_check = db.Column(db.DateTime, nullable=True)
    group = db.Column(db.String(50), default='交换机')  # 新增分组字段
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'username': self.username,
            'password': self.password,
            'enable_password': self.enable_password,
            'device_type': self.device_type,
            'protocol': self.protocol,
            'commands': self.commands,
            'status': self.status,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'group': self.group,
            'created_at': self.created_at.isoformat()
        }

# 巡检记录模型
class InspectionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    result = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'result': self.result,
            'created_at': self.created_at.isoformat()
        }

# 创建数据库表
with app.app_context():
    try:
        db.create_all()
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {str(e)}")
        raise

def get_device_type(device_type, protocol):
    """根据设备类型和协议返回netmiko设备类型"""
    if protocol.lower() == 'telnet':
        return f"{device_type}_telnet"
    return device_type

def check_device_status(device):
    """检查设备状态"""
    try:
        # 根据操作系统选择ping命令
        if platform.system().lower() == 'windows':
            ping_cmd = f'ping -n 1 -w 1000 {device.ip}'
        else:
            ping_cmd = f'ping -c 1 -W 1 {device.ip}'
            
        result = subprocess.run(ping_cmd, shell=True, capture_output=True, text=True)
        device.status = 'online' if result.returncode == 0 else 'offline'
        device.last_check = datetime.now(tz)
        db.session.commit()
    except Exception as e:
        print(f"检查设备 {device.ip} 状态时出错: {str(e)}")
        device.status = 'offline'
        device.last_check = datetime.now(tz)
        db.session.commit()

def check_all_devices():
    """检查所有设备状态"""
    while True:
        with app.app_context():
            devices = Device.query.all()
            for device in devices:
                check_device_status(device)
        time.sleep(30)  # 每30秒检查一次

# 启动状态检查线程
status_check_thread = threading.Thread(target=check_all_devices, daemon=True)
status_check_thread.start()

# API路由
@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        devices = Device.query.all()
        logger.info(f"成功获取设备列表，共{len(devices)}个设备")
        return jsonify([device.to_dict() for device in devices])
    except Exception as e:
        logger.error(f"获取设备列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices', methods=['POST'])
def add_device():
    try:
        data = request.json
        
        # 处理commands字段，确保存储格式正确
        commands = data.get('commands', '')
        # 如果commands是JSON字符串，尝试解析并转换为逗号分隔的字符串
        try:
            if isinstance(commands, str) and commands.startswith('[') and commands.endswith(']'):
                commands_list = json.loads(commands)
                commands = ','.join([str(cmd).strip() for cmd in commands_list if cmd])
        except:
            # 如果解析失败，保持原样
            pass
        
        device = Device(
            name=data['name'],
            ip=data['ip'],
            username=data['username'],
            password=data['password'],
            enable_password=data.get('enable_password'),
            device_type=data['device_type'],
            protocol=data['protocol'],
            commands=commands,
            group=data.get('group', '交换机')  # 新增分组字段，默认为"交换机"
        )
        db.session.add(device)
        db.session.commit()
        logger.info(f"成功添加设备: {device.name}")
        return jsonify(device.to_dict())
    except Exception as e:
        logger.error(f"添加设备失败: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    return '', 204

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    try:
        device = Device.query.get_or_404(device_id)
        data = request.json
        
        # 处理commands字段，确保存储格式正确
        commands = data.get('commands', '')
        # 如果commands是JSON字符串，尝试解析并转换为逗号分隔的字符串
        try:
            if isinstance(commands, str) and commands.startswith('[') and commands.endswith(']'):
                commands_list = json.loads(commands)
                commands = ','.join([str(cmd).strip() for cmd in commands_list if cmd])
        except:
            # 如果解析失败，保持原样
            pass
        
        # 更新设备信息
        device.name = data['name']
        device.ip = data['ip']
        device.username = data['username']
        device.password = data['password']
        device.enable_password = data.get('enable_password')
        device.device_type = data['device_type']
        device.protocol = data['protocol']
        device.commands = commands
        device.group = data.get('group', '交换机')  # 新增分组字段，默认为"交换机"
        
        db.session.commit()
        logger.info(f"成功更新设备: {device.name}")
        return jsonify(device.to_dict())
    except Exception as e:
        logger.error(f"更新设备失败: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/<int:device_id>/inspect', methods=['POST'])
def inspect_device(device_id):
    device = Device.query.get_or_404(device_id)
    
    # 检查设备状态
    if device.status != 'online':
        return jsonify({
            'success': False,
            'message': f'设备 {device.name} ({device.ip}) 当前不在线，无法执行巡检'
        }), 400

    try:
        # 获取设备类型
        device_type = get_device_type(device.device_type, device.protocol)
        
        logger.info(f"开始巡检设备: {device.name} ({device.ip}), 设备类型: {device_type}")
        
        # 连接设备
        connection_params = {
            'device_type': device_type,
            'host': device.ip,
            'username': device.username,
            'password': device.password,
            'timeout': 20,
            'auth_timeout': 20,
            'banner_timeout': 20,
            'fast_cli': False
        }
        
        # 如果配置了enable密码，添加到连接参数中
        if device.enable_password and device.enable_password.strip():
            connection_params['secret'] = device.enable_password
        
        # 建立连接
        logger.info(f"正在连接设备: {device.ip}")
        connection = netmiko.ConnectHandler(**connection_params)
        logger.info(f"成功连接到设备: {device.ip}")
        
        # 如果是Cisco IOS设备并且有enable密码，进入enable模式
        if 'cisco_ios' in device_type and device.enable_password and device.enable_password.strip():
            logger.info(f"正在进入enable模式: {device.ip}")
            connection.enable()
            logger.info(f"已进入enable模式: {device.ip}")
        elif 'ruijie_os' in device_type:
            logger.info(f"锐捷交换机设备 {device.ip} 不需要进入 enable 模式，跳过此步骤")
        
        # 解析并执行巡检命令
        results = []
        try:
            # 尝试解析命令
            try:
                if device.commands.startswith('[') and device.commands.endswith(']'):
                    # 如果命令是JSON数组格式
                    commands_list = json.loads(device.commands)
                    # 确保每个命令都是纯文本字符串
                    commands = [str(cmd).strip() for cmd in commands_list if cmd]
                else:
                    # 如果不是JSON格式，尝试按逗号分隔
                    commands = [cmd.strip() for cmd in device.commands.split(',') if cmd.strip()]
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试按逗号分隔处理
                commands = [cmd.strip() for cmd in device.commands.split(',') if cmd.strip()]
            except Exception as e:
                logger.error(f"命令解析错误: {str(e)}")
                # 如果所有尝试都失败，将整个commands作为单个命令
                commands = [device.commands] if device.commands else []
            
            # 确保commands是列表类型且每个命令都是纯文本字符串
            if not isinstance(commands, list):
                commands = [str(commands)] if commands else []
            else:
                commands = [str(cmd) for cmd in commands]
            
            # 清理命令，移除所有可能的特殊字符和格式
            cleaned_commands = []
            for cmd in commands:
                # 移除所有可能的引号（单引号和双引号）
                cmd = cmd.replace('"', '').replace("'", '')
                # 移除所有可能的方括号
                cmd = cmd.replace('[', '').replace(']', '')
                # 移除命令前后的空白字符
                cmd = cmd.strip()
                # 如果命令不为空，添加到清理后的命令列表
                if cmd:
                    cleaned_commands.append(cmd)
            
            commands = cleaned_commands
            logger.info(f"清理后的设备 {device.ip} 的巡检命令: {commands}")
            
            # 执行每个命令
            for cmd in commands:
                try:
                    logger.info(f"正在执行命令: {cmd}")
                    output = connection.send_command(cmd, strip_prompt=False, strip_command=False)
                    logger.info(f"命令 {cmd} 执行成功")
                    results.append({
                        'command': cmd,
                        'output': output
                    })
                except Exception as e:
                    error_msg = f"执行命令 {cmd} 失败: {str(e)}"
                    logger.error(error_msg)
                    results.append({
                        'command': cmd,
                        'output': error_msg
                    })
        except Exception as e:
            error_msg = f"处理巡检命令时出错: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'message': error_msg
            }), 400
        
        # 断开连接
        connection.disconnect()
        logger.info(f"已断开与设备 {device.ip} 的连接")
        
        # 保存巡检记录
        try:
            record = InspectionRecord(
                device_id=device.id,
                device_name=device.name,
                result=json.dumps(results, ensure_ascii=False)
            )
            db.session.add(record)
            db.session.commit()
            logger.info(f"设备 {device.name} ({device.ip}) 巡检完成，已保存记录")
            
            # 验证记录是否成功保存
            saved_record = InspectionRecord.query.get(record.id)
            if saved_record:
                logger.info(f"巡检记录保存成功，ID: {record.id}")
            else:
                logger.error("巡检记录保存失败，无法查询到记录")
        except Exception as e:
            logger.error(f"保存巡检记录时出错: {str(e)}")
            db.session.rollback()
            raise
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except netmiko.ssh_exception.NetMikoTimeoutException as e:
        error_msg = f'连接设备 {device.name} ({device.ip}) 超时，请检查网络连接或设备是否可达: {str(e)}'
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500
    except netmiko.ssh_exception.NetMikoAuthenticationException as e:
        error_msg = f'设备 {device.name} ({device.ip}) 认证失败，请检查用户名和密码是否正确: {str(e)}'
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500
    except Exception as e:
        error_msg = f'巡检设备 {device.name} ({device.ip}) 失败: {str(e)}'
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'message': error_msg
        }), 500

@app.route('/api/devices/<int:device_id>/records', methods=['GET'])
def get_device_records(device_id):
    try:
        # 检查设备是否存在
        device = Device.query.get_or_404(device_id)
        # 获取该设备的所有巡检记录，按时间倒序排序
        records = InspectionRecord.query.filter_by(device_id=device_id).order_by(InspectionRecord.created_at.desc()).all()
        logger.info(f"成功获取设备 {device.name} 的巡检记录，共 {len(records)} 条")
        return jsonify([record.to_dict() for record in records])
    except Exception as e:
        logger.error(f"获取设备 {device_id} 的巡检记录失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    try:
        # 查找巡检记录
        record = InspectionRecord.query.get_or_404(record_id)
        # 记录相关信息
        device_name = record.device_name
        device_id = record.device_id
        # 删除记录
        db.session.delete(record)
        db.session.commit()
        logger.info(f"成功删除设备 {device_name} (ID: {device_id}) 的巡检记录 (ID: {record_id})")
        return jsonify({'success': True, 'message': '巡检记录删除成功'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除巡检记录 {record_id} 失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

# 添加导入导出API
@app.route('/api/devices/export', methods=['GET'])
def export_devices():
    try:
        devices = Device.query.all()
        data = []
        for device in devices:
            data.append({
                '设备名称': device.name,
                'IP地址': device.ip,
                '用户名': device.username,
                '密码': device.password,
                'Enable密码': device.enable_password or '',
                '设备类型': device.device_type,
                '连接协议': device.protocol,
                '巡检命令': device.commands,
                '设备分组': device.group
            })
        
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='设备列表')
        
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='设备列表.xlsx'
        )
    except Exception as e:
        logger.error(f"导出设备列表失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/devices/import', methods=['POST'])
def import_devices():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未找到上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '未选择文件'}), 400
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'success': False, 'error': '只能上传.xlsx格式的文件'}), 400
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file)
        
        # 检查必要的列是否存在
        required_columns = ['设备名称', 'IP地址', '用户名', '密码', '设备类型', '连接协议', '巡检命令']
        for col in required_columns:
            if col not in df.columns:
                return jsonify({'success': False, 'error': f'Excel文件缺少"{col}"列'}), 400
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 遍历行并导入设备
        for index, row in df.iterrows():
            try:
                # 检查设备是否已存在（按IP地址检查）
                existing_device = Device.query.filter_by(ip=row['IP地址']).first()
                if existing_device:
                    # 更新现有设备
                    existing_device.name = row['设备名称']
                    existing_device.username = row['用户名']
                    existing_device.password = row['密码']
                    existing_device.enable_password = row['Enable密码'] if 'Enable密码' in row and not pd.isna(row['Enable密码']) else None
                    existing_device.device_type = row['设备类型']
                    existing_device.protocol = row['连接协议']
                    existing_device.commands = row['巡检命令']
                    existing_device.group = row['设备分组'] if '设备分组' in row and not pd.isna(row['设备分组']) else '交换机'
                else:
                    # 创建新设备
                    new_device = Device(
                        name=row['设备名称'],
                        ip=row['IP地址'],
                        username=row['用户名'],
                        password=row['密码'],
                        enable_password=row['Enable密码'] if 'Enable密码' in row and not pd.isna(row['Enable密码']) else None,
                        device_type=row['设备类型'],
                        protocol=row['连接协议'],
                        commands=row['巡检命令'],
                        group=row['设备分组'] if '设备分组' in row and not pd.isna(row['设备分组']) else '交换机'
                    )
                    db.session.add(new_device)
                
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"行 {index+2}: {str(e)}")
        
        db.session.commit()
        logger.info(f"设备导入完成，成功: {success_count}，失败: {error_count}")
        
        return jsonify({
            'success': True,
            'message': f'导入完成，成功导入 {success_count} 个设备',
            'error_count': error_count,
            'errors': errors
        })
    except Exception as e:
        logger.error(f"导入设备数据失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/records/<int:record_id>/export', methods=['GET'])
def export_record(record_id):
    try:
        # 获取巡检记录
        record = InspectionRecord.query.get_or_404(record_id)
        
        # 获取设备信息
        device = Device.query.get(record.device_id)
        
        # 解析巡检结果
        try:
            results = json.loads(record.result)
        except Exception as e:
            logger.error(f"解析巡检结果失败: {str(e)}")
            return jsonify({'error': f"解析巡检结果失败: {str(e)}"}), 500
        
        # 将巡检结果格式化为文本
        content = []
        content.append(f"设备名称: {record.device_name}")
        content.append(f"设备IP: {device.ip if device else '未知'}")
        content.append(f"巡检时间: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("="*50)
        
        for item in results:
            content.append(f"\n[命令] {item['command']}")
            content.append("-"*50)
            content.append(f"{item['output']}")
            content.append("-"*50)
        
        # 创建文件名
        device_ip = device.ip if device else "unknown"
        timestamp = record.created_at.strftime("%Y%m%d_%H%M%S")
        filename = f"{record.device_name}_{device_ip}_{timestamp}.txt"
        
        # 创建内存文件
        output = io.StringIO()
        output.write("\n".join(content))
        output.seek(0)
        
        # 发送文件
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"导出巡检记录失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/batch-export', methods=['GET'])
def batch_export_records():
    try:
        # 获取要导出的记录ID列表
        record_ids = request.args.getlist('id', type=int)
        
        if not record_ids:
            return jsonify({'error': '未指定要导出的记录ID'}), 400
        
        # 创建ZIP文件
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for record_id in record_ids:
                try:
                    # 获取巡检记录
                    record = InspectionRecord.query.get(record_id)
                    if not record:
                        logger.warning(f"巡检记录 {record_id} 不存在")
                        continue
                    
                    # 获取设备信息
                    device = Device.query.get(record.device_id)
                    
                    # 解析巡检结果
                    try:
                        results = json.loads(record.result)
                    except:
                        logger.warning(f"解析巡检记录 {record_id} 结果失败")
                        continue
                    
                    # 将巡检结果格式化为文本
                    content = []
                    content.append(f"设备名称: {record.device_name}")
                    content.append(f"设备IP: {device.ip if device else '未知'}")
                    content.append(f"巡检时间: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    content.append("="*50)
                    
                    for item in results:
                        content.append(f"\n[命令] {item['command']}")
                        content.append("-"*50)
                        content.append(f"{item['output']}")
                        content.append("-"*50)
                    
                    # 创建文件名
                    device_ip = device.ip if device else "unknown"
                    timestamp = record.created_at.strftime("%Y%m%d_%H%M%S")
                    filename = f"{record.device_name}_{device_ip}_{timestamp}.txt"
                    
                    # 添加到ZIP文件
                    zf.writestr(filename, "\n".join(content))
                    
                except Exception as e:
                    logger.error(f"处理记录 {record_id} 时出错: {str(e)}")
                    continue
        
        # 准备发送ZIP文件
        memory_file.seek(0)
        timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'inspection_records_{timestamp}.zip'
        )
    except Exception as e:
        logger.error(f"批量导出巡检记录失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("启动华巡巡检系统后端服务")
    app.run(debug=True, host='0.0.0.0', port=5000) 