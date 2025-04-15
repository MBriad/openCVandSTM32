#include "stm32f10x.h" // Device header
#include <stdint.h>
#include "stm32f10x_tim.h"
#include "Delay.h"
#include "OLED.h"
#include "Serial.h"
#include "Timer.h"

uint8_t RxData;
uint16_t Num = 0;

int main(void)
{
    OLED_Init();
    Serial_Init();
    OLED_ShowString(1, 1, "RxData:");
    Timer_Init();
    OLED_ShowString(2, 1, "Time:");
    while (1) {
        if (Serial_GetRxFlag() == 1) {
            RxData = Serial_GetRxData();
            OLED_ShowHexNum(1, 8, RxData, 2);
            Serial_SendByte(RxData);
        }
        OLED_ShowNum(2, 5, Timer_GetCounter(), 5);
        Delay_ms(10);
    }
}

void TIM2_IRQHandler(void)
{
    if (TIM_GetITStatus(TIM2, TIM_IT_Update) == SET) {
        Num++;
        TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
    }
}