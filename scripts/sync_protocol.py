#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import serial
import time
import logging
import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("protocol_test.log"),
        logging.StreamHandler()
    ]
)

@dataclass
class ProtocolCommand:
    """协议命令数据类"""
    char: str
    description: str
    expected_led: str
    expected_display: str

class ProtocolTester:
    """协议测试类"""
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None
        
        # 定义协议命令
        self.commands: Dict[str, ProtocolCommand] = {
            'A': ProtocolCommand('A', '检测到物体A', 'LED1亮,LED2灭', 'Object A'),
            'B': ProtocolCommand('B', '检测到物体B', 'LED2亮,LED1灭', 'Object B'),
            'N': ProtocolCommand('N', '未检测到物体', 'LED1灭,LED2灭', 'No Object')
        }

    def connect(self) -> bool:
        """连接串口"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1
            )
            logging.info(f"成功连接到串口 {self.port}")
            return True
        except serial.SerialException as e:
            logging.error(f"串口连接失败: {e}")
            return False

    def disconnect(self):
        """断开串口连接"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("串口连接已关闭")

    def send_command(self, cmd: str) -> bool:
        """发送命令"""
        if not self.ser or not self.ser.is_open:
            logging.error("串口未连接")
            return False
        
        try:
            self.ser.write(cmd.encode())
            logging.info(f"发送命令: {cmd} ({self.commands[cmd].description})")
            return True
        except Exception as e:
            logging.error(f"发送命令失败: {e}")
            return False

    def read_response(self, timeout: float = 1.0) -> Optional[str]:
        """读取STM32的响应"""
        if not self.ser or not self.ser.is_open:
            logging.error("串口未连接")
            return None
        
        try:
            # 设置读取超时
            self.ser.timeout = timeout
            response = self.ser.readline().decode().strip()
            if response:
                logging.info(f"收到响应: {response}")
                return response
            return None
        except Exception as e:
            logging.error(f"读取响应失败: {e}")
            return None

    def test_protocol(self) -> bool:
        """测试完整协议"""
        if not self.connect():
            return False

        try:
            # 测试所有命令
            for cmd in self.commands.values():
                logging.info(f"\n--- 测试命令: {cmd.char} ---")
                logging.info(f"预期行为: LED状态={cmd.expected_led}, 显示={cmd.expected_display}")
                
                if not self.send_command(cmd.char):
                    return False
                
                # 等待STM32处理
                time.sleep(0.5)
                
                # 读取STM32的响应
                response = self.read_response()
                if response:
                    if response.startswith("ACK_"):
                        logging.info(f"命令 {cmd.char} 测试成功")
                    else:
                        logging.warning(f"命令 {cmd.char} 收到非预期响应: {response}")
                else:
                    logging.warning(f"命令 {cmd.char} 未收到响应")
                
            logging.info("\n所有命令测试完成")
            return True

        except Exception as e:
            logging.error(f"测试过程出错: {e}")
            return False
        
        finally:
            self.disconnect()

    def stress_test(self, cycles: int = 100) -> bool:
        """压力测试"""
        if not self.connect():
            return False

        try:
            logging.info(f"\n开始压力测试 ({cycles} 循环)")
            success_count = 0
            fail_count = 0
            
            for i in range(cycles):
                for cmd in ['A', 'B', 'N']:
                    if not self.send_command(cmd):
                        fail_count += 1
                        continue
                    
                    # 等待STM32处理
                    time.sleep(0.1)
                    
                    # 读取响应
                    response = self.read_response(timeout=0.5)
                    if response and response.startswith("ACK_"):
                        success_count += 1
                    else:
                        fail_count += 1
                
                if (i + 1) % 10 == 0:
                    logging.info(f"完成 {i + 1} 个循环, 成功: {success_count}, 失败: {fail_count}")
            
            logging.info(f"压力测试完成, 总成功: {success_count}, 总失败: {fail_count}")
            return fail_count == 0

        except Exception as e:
            logging.error(f"压力测试失败: {e}")
            return False
        
        finally:
            self.disconnect()

    def auto_test(self) -> bool:
        """自动测试模式"""
        if not self.connect():
            return False

        try:
            logging.info("开始自动测试模式")
            
            # 发送系统就绪信息
            self.send_command('N')
            time.sleep(0.5)
            
            # 测试物体A
            self.send_command('A')
            time.sleep(1)
            
            # 测试物体B
            self.send_command('B')
            time.sleep(1)
            
            # 测试无物体
            self.send_command('N')
            time.sleep(1)
            
            # 快速切换测试
            for _ in range(5):
                self.send_command('A')
                time.sleep(0.2)
                self.send_command('B')
                time.sleep(0.2)
                self.send_command('N')
                time.sleep(0.2)
            
            logging.info("自动测试完成")
            return True

        except Exception as e:
            logging.error(f"自动测试失败: {e}")
            return False
        
        finally:
            self.disconnect()

def find_available_ports() -> List[str]:
    """查找可用的串口"""
    import serial.tools.list_ports
    
    ports = []
    for port in serial.tools.list_ports.comports():
        ports.append(port.device)
    
    return ports

def main():
    """主函数"""
    # 查找可用串口
    available_ports = find_available_ports()
    
    if not available_ports:
        logging.error("未找到可用串口")
        print("未找到可用串口，请检查设备连接")
        return
    
    # 获取串口参数
    if len(sys.argv) > 1:
        port = sys.argv[1]
        if port not in available_ports:
            logging.warning(f"指定的串口 {port} 不可用，将使用默认串口")
            port = available_ports[0]
    else:
        port = available_ports[0]  # 使用第一个可用串口
    
    print(f"\n可用串口: {', '.join(available_ports)}")
    print(f"使用串口: {port}")
    
    tester = ProtocolTester(port)
    
    print("\n=== STM32-PC 通信协议测试工具 ===")
    print("1. 基本协议测试")
    print("2. 压力测试")
    print("3. 自动测试")
    print("4. 退出")
    
    while True:
        choice = input("\n请选择测试类型 (1-4): ")
        
        if choice == '1':
            tester.test_protocol()
        elif choice == '2':
            cycles = int(input("请输入测试循环次数: "))
            tester.stress_test(cycles)
        elif choice == '3':
            tester.auto_test()
        elif choice == '4':
            print("程序退出")
            break
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    main()
