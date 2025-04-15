/**
 ******************************************************************************
 * @file    stm32f10x.h
 * @author  MCD Application Team
 * @version V3.5.0
 * @date    11-March-2011
 * @brief   CMSIS Cortex-M3 Device Peripheral Access Layer Header File.
 *          This file contains all the peripheral register's definitions, bits
 *          definitions and memory mapping for STM32F10x Connectivity line,
 *          High density, High density value line, Medium density,
 *          Medium density Value line, Low density, Low density Value line
 *          and XL-density devices.
 *
 *          The file is the unique include file that the application programmer
 *          is using in the C source code, usually in main.c. This file contains:
 *           - Configuration section that allows to select:
 *              - The device used in the target application
 *              - To use or not the peripheral's drivers in application code(i.e.
 *                code will be based on direct access to peripheral's registers
 *                rather than drivers API), this option is controlled by
 *                "#define USE_STDPERIPH_DRIVER"
 *              - To change few application-specific parameters such as the HSE
 *                crystal frequency
 *           - Data structures and the address mapping for all peripherals
 *           - Peripheral's registers declarations and bits definition
 *           - Macros to access peripheral's registers hardware
 *
 ******************************************************************************
 * @attention
 *
 * THE PRESENT FIRMWARE WHICH IS FOR GUIDANCE ONLY AIMS AT PROVIDING CUSTOMERS
 * WITH CODING INFORMATION REGARDING THEIR PRODUCTS IN ORDER FOR THEM TO SAVE
 * TIME. AS A RESULT, STMICROELECTRONICS SHALL NOT BE HELD LIABLE FOR ANY
 * DIRECT, INDIRECT OR CONSEQUENTIAL DAMAGES WITH RESPECT TO ANY CLAIMS ARISING
 * FROM THE CONTENT OF SUCH FIRMWARE AND/OR THE USE MADE BY CUSTOMERS OF THE
 * CODING INFORMATION CONTAINED HEREIN IN CONNECTION WITH THEIR PRODUCTS.
 *
 * <h2><center>&copy; COPYRIGHT 2011 STMicroelectronics</center></h2>
 ******************************************************************************
 */

/** @addtogroup CMSIS
 * @{
 */

/** @addtogroup stm32f10x
 * @{
 */

#ifndef __STM32F10x_H
#define __STM32F10x_H

#ifdef __cplusplus
extern "C" {
#endif

/** @addtogroup Library_configuration_section
 * @{
 */

/* Uncomment the line below according to the target STM32 device used in your
   application
  */

#if !defined(STM32F10X_LD) && !defined(STM32F10X_LD_VL) && !defined(STM32F10X_MD) && !defined(STM32F10X_MD_VL) && !defined(STM32F10X_HD) && !defined(STM32F10X_HD_VL) && !defined(STM32F10X_XL) && !defined(STM32F10X_CL)
/* #define STM32F10X_LD */    /*!< STM32F10X_LD: STM32 Low density devices */
/* #define STM32F10X_LD_VL */ /*!< STM32F10X_LD_VL: STM32 Low density Value Line devices */
#define STM32F10X_MD          /*!< STM32F10X_MD: STM32 Medium density devices */
/* #define STM32F10X_MD_VL */ /*!< STM32F10X_MD_VL: STM32 Medium density Value Line devices */
/* #define STM32F10X_HD */    /*!< STM32F10X_HD: STM32 High density devices */
/* #define STM32F10X_HD_VL */ /*!< STM32F10X_HD_VL: STM32 High density value line devices */
/* #define STM32F10X_XL */    /*!< STM32F10X_XL: STM32 XL-density devices */
/* #define STM32F10X_CL */    /*!< STM32F10X_CL: STM32 Connectivity line devices */
#endif

// 这里省略了大部分内容
// 实际项目中需要将完整的stm32f10x.h文件内容复制到这里
// 由于篇幅限制，这里只展示部分内容

#ifdef __cplusplus
}
#endif

#endif /* __STM32F10x_H */

/**
 * @}
 */

/**
 * @}
 */

/******************* (C) COPYRIGHT 2011 STMicroelectronics *****END OF FILE****/