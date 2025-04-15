#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time
import logging
from typing import Optional

class CommunicationProtocol:
    """通信协议类，处理与STM32的串口通信"""
    
    # 定义协议命令
    CMD_OBJECT_A = 'A'  # 检测到物体A
    CMD_OBJECT_B = 'B'  # 检测到物体B
    CMD_NO_OBJECT = 'N' # 未检测到物体
    
    # 定义响应前缀
    ACK_PREFIX = "ACK_"
    ERR_PREFIX = "ERR:"
    
    def __init__(self, port: str = 'COM3', baudrate: int = 115200):
        """
        初始化通信协议
        :param port: 串口号
        :param baudrate: 波特率
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志"""
        self.logger = logging.getLogger('CommunicationProtocol')
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def connect(self) -> bool:
        """
        连接串口
        :return: 是否连接成功
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            self.logger.info(f"成功连接到串口 {self.port}")
            return True
        except Exception as e:
            self.logger.error(f"串口连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开串口连接"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("串口连接已关闭")
    
    def send_command(self, command: str) -> bool:
        """
        发送命令到STM32
        :param command: 命令字符
        :return: 是否发送成功
        """
        if not self.serial or not self.serial.is_open:
            self.logger.error("串口未连接")
            return False
        
        try:
            self.serial.write(command.encode())
            self.logger.debug(f"发送命令: {command}")
            return True
        except Exception as e:
            self.logger.error(f"发送命令失败: {e}")
            return False
    
    def read_response(self, timeout: float = 1.0) -> Optional[str]:
        """
        读取STM32的响应
        :param timeout: 超时时间（秒）
        :return: 响应字符串，超时或错误返回None
        """
        if not self.serial or not self.serial.is_open:
            self.logger.error("串口未连接")
            return None
        
        try:
            self.serial.timeout = timeout
            response = self.serial.readline().decode().strip()
            if response:
                self.logger.debug(f"收到响应: {response}")
                return response
            return None
        except Exception as e:
            self.logger.error(f"读取响应失败: {e}")
            return None
    
    def send_object_detected(self, object_type: str) -> bool:
        """
        发送物体检测结果
        :param object_type: 'A' 或 'B' 或 'N'
        :return: 是否发送成功
        """
        if object_type not in [self.CMD_OBJECT_A, self.CMD_OBJECT_B, self.CMD_NO_OBJECT]:
            self.logger.error(f"无效的物体类型: {object_type}")
            return False
        
        success = self.send_command(object_type)
        if success:
            # 等待并验证响应
            response = self.read_response()
            if response and response.startswith(self.ACK_PREFIX):
                self.logger.info(f"物体{object_type}检测命令已确认")
                return True
            else:
                self.logger.warning("未收到有效确认")
                return False
        return False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect()

def main():
    """测试函数"""
    # 测试代码
    with CommunicationProtocol() as protocol:
        # 测试发送物体A
        protocol.send_object_detected('A')
        time.sleep(1)
        
        # 测试发送物体B
        protocol.send_object_detected('B')
        time.sleep(1)
        
        # 测试发送无物体
        protocol.send_object_detected('N')

if __name__ == "__main__":
    main()
