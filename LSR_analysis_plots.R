

library(tidyverse)
library(ggpubr)
library(readxl)

LSR_MjerenjaTemp <- read_excel("~/Desktop/LSR_MjerenjaTemp.xlsx", sheet = "24to12", skip = 1)


p1 <- ggplot(LSR_MjerenjaTemp) +
  geom_point(aes(x = TimeInMinPassed, y=LSRBlockTemp, color = "LSR")) +
  geom_line(aes(x = TimeInMinPassed, y=LSRBlockTemp, color = "LSR")) +
  geom_point(aes(x = TimeInMinPassed, y=ExternalSensorTemp, color = "External Sensor")) +
  geom_line(aes(x = TimeInMinPassed, y=ExternalSensorTemp, color = "External Sensor")) +
  xlab("Time Passed (min)") + ylab("Temp (C)") + 
  scale_color_hue(l=40, c=75) +
  ggtitle("24C to 12C")+ 
  theme_pubclean()


p2 <- ggplot(LSR_MjerenjaTemp) +
  geom_point(aes(x = TimeInMinPassed, y=DeltaLSRBlockTemp, color = "Delta LSR")) +
  geom_line(aes(x = TimeInMinPassed, y=DeltaLSRBlockTemp, color = "Delta LSR")) +
  geom_point(aes(x = TimeInMinPassed, y=DeltaExternalSensorTemp, color = "Delta External Sensor")) +
  geom_line(aes(x = TimeInMinPassed, y=DeltaExternalSensorTemp, color = "Delta External Sensor")) +
  xlab("Time Passed (min)") + ylab("Delta Temp (C)") +
  scale_color_hue(l=40, c=75) +
  theme_pubclean()

p3 <- ggplot(LSR_MjerenjaTemp) +
  geom_point(aes(x = TimeInMinPassed, y=DiffBetweenLSRAndSensor)) +
  geom_line(aes(x = TimeInMinPassed, y=DiffBetweenLSRAndSensor)) +
  xlab("Time Passed (min)") + ylab("Delta LSR - Sensor") +
  theme_pubclean()

LSR_MjerenjaTemp <- read_excel("~/Desktop/LSR_MjerenjaTemp.xlsx", sheet = "12to28", skip = 1)
p4 <- ggplot(LSR_MjerenjaTemp) +
  geom_point(aes(x = TimeInMinPassed, y=LSRBlockTemp, color = "LSR")) +
  geom_line(aes(x = TimeInMinPassed, y=LSRBlockTemp, color = "LSR")) +
  geom_point(aes(x = TimeInMinPassed, y=ExternalSensorTemp, color = "External Sensor")) +
  geom_line(aes(x = TimeInMinPassed, y=ExternalSensorTemp, color = "External Sensor")) +
  xlab("Time Passed (min)") + ylab("Temp (C)") + 
  ggtitle("12C to 28C")+ 
  scale_color_hue(l=40, c=75) +
  theme_pubclean()


p5 <- ggplot(LSR_MjerenjaTemp) +
  geom_point(aes(x = TimeInMinPassed, y=DeltaLSRBlockTemp, color = "Delta LSR")) +
  geom_line(aes(x = TimeInMinPassed, y=DeltaLSRBlockTemp, color = "Delta LSR")) +
  geom_point(aes(x = TimeInMinPassed, y=DeltaExternalSensorTemp, color = "Delta External Sensor")) +
  geom_line(aes(x = TimeInMinPassed, y=DeltaExternalSensorTemp, color = "Delta External Sensor")) +
  xlab("Time Passed (min)") + ylab("Delta Temp (C)") +
  scale_color_hue(l=40, c=75) +
  theme_pubclean()

p6 <- ggplot(LSR_MjerenjaTemp) +
  geom_point(aes(x = TimeInMinPassed, y=DiffBetweenLSRAndSensor)) +
  geom_line(aes(x = TimeInMinPassed, y=DiffBetweenLSRAndSensor)) +
  xlab("Time Passed (min)") + ylab("Delta LSR - Sensor") +
  theme_pubclean()

ggarrange(p1,p2,p3,p4,p5,p6, nrow = 2, ncol = 3)