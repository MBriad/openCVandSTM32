#include "protocol.h"
#include "usart.h"
#include "gpio.h"

/* LED控制实现 */
void LED_Toggle(uint8_t led)
{
    if (led == 1)
        HAL_GPIO_TogglePin(LED1_GPIO_Port, LED1_Pin);
    else if (led == 2)
        HAL_GPIO_TogglePin(LED2_GPIO_Port, LED2_Pin);
}

void LED_Blink(uint8_t led, uint16_t times)
{
    for (uint16_t i = 0; i < times; i++) {
        LED_Toggle(led);
        HAL_Delay(200);
        LED_Toggle(led);
        HAL_Delay(200);
    }
}

void LED1_ON(void)
{
    HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, GPIO_PIN_SET);
}

void LED1_OFF(void)
{
    HAL_GPIO_WritePin(LED1_GPIO_Port, LED1_Pin, GPIO_PIN_RESET);
}

void LED2_ON(void)
{
    HAL_GPIO_WritePin(LED2_GPIO_Port, LED2_Pin, GPIO_PIN_SET);
}

void LED2_OFF(void)
{
    HAL_GPIO_WritePin(LED2_GPIO_Port, LED2_Pin, GPIO_PIN_RESET);
}

/* 协议处理实现 */
void Protocol_Init(void)
{
    // 初始化UART
    MX_USART1_UART_Init();
}

void Send_Response(const char *response)
{
    HAL_UART_Transmit(&huart1, (uint8_t *)response, strlen(response), 100);
}

void Handle_Protocol(uint8_t data)
{
    switch (data) {
        case CMD_OBJECT_A:
            handle_object_A();
            break;
        case CMD_OBJECT_B:
            handle_object_B();
            break;
        case CMD_NO_OBJECT:
            handle_no_object();
            break;
        default:
            Send_Response(ERR_MSG);
            break;
    }
}

/* 物体处理实现 */
void handle_object_A(void)
{
    LED1_ON();
    LED2_OFF();
    Send_Response(ACK_A);
}

void handle_object_B(void)
{
    LED1_OFF();
    LED2_ON();
    Send_Response(ACK_B);
}

void handle_no_object(void)
{
    LED1_OFF();
    LED2_OFF();
    Send_Response(ACK_N);
}