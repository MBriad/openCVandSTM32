#ifndef __PROTOCOL_H
#define __PROTOCOL_H

#include "stm32f10x.h"

/* 协议命令定义 */
#define CMD_OBJECT_A  'A' // 检测到物体A
#define CMD_OBJECT_B  'B' // 检测到物体B
#define CMD_NO_OBJECT 'N' // 未检测到物体

/* 响应定义 */
#define ACK_A   "ACK_A\r\n" // 确认收到A命令
#define ACK_B   "ACK_B\r\n" // 确认收到B命令
#define ACK_N   "ACK_N\r\n" // 确认收到N命令
#define ERR_MSG "ERR\r\n"   // 错误响应

/* LED控制函数 */
void LED_Toggle(uint8_t led);
void LED_Blink(uint8_t led, uint16_t times);
void LED1_ON(void);
void LED1_OFF(void);
void LED2_ON(void);
void LED2_OFF(void);

/* 协议处理函数 */
void Protocol_Init(void);
void Protocol_Process(uint8_t cmd);
void Send_Response(const char *response);
void Handle_Protocol(uint8_t data);

/* 物体处理函数 */
void handle_object_A(void);
void handle_object_B(void);
void handle_no_object(void);

#endif /* __PROTOCOL_H */

void LED_Toggle(uint8_t led)
{
    switch (led) {
        case 1:
            GPIO_WriteBit(LED1_PORT, LED1_PIN,
                          (BitAction)!GPIO_ReadOutputDataBit(LED1_PORT, LED1_PIN));
            break;
        case 2:
            GPIO_WriteBit(LED2_PORT, LED2_PIN,
                          (BitAction)!GPIO_ReadOutputDataBit(LED2_PORT, LED2_PIN));
            break;
    }
}

void LED_Blink(uint8_t led, uint16_t times)
{
    uint16_t i;
    for (i = 0; i < times; i++) {
        LED_Toggle(led);
        delay_ms(200); // 需要实现delay_ms函数
    }
}

void Handle_Protocol(uint8_t data)
{
    static uint8_t last_state = 0;

    switch (data) {
        case 'A':
            if (last_state != 'A') {
                handle_object_A();
                UART1_SendString("ACK_A\r\n");
                last_state = 'A';
            }
            break;

        case 'B':
            if (last_state != 'B') {
                handle_object_B();
                UART1_SendString("ACK_B\r\n");
                last_state = 'B';
            }
            break;

        case 'N':
            if (last_state != 'N') {
                handle_no_object();
                UART1_SendString("ACK_N\r\n");
                last_state = 'N';
            }
            break;

        default:
            UART1_SendString("ERR:Invalid Command\r\n");
            break;
    }
}
