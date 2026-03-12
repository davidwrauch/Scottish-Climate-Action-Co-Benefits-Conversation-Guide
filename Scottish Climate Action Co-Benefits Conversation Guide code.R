install.packages("corrr")

library(ggplot2)
library(randomForest)
library(caret)
library(corrr)
library(readxl)
library(lubridate)
library(tidyverse)
library(data.table)
library(dplyr)
library(readr)
library(stringr)
library(stringi)
library(openxlsx)
library(rpart.plot)
library(rpart)

setwd("C:/data exercises/Edinburgh")

options(scipen = 999)

climate_action_data <- read_excel('Edinburgh climate change comp Level_1.xlsx')

names(climate_action_data)

SC_climate_action_data <- climate_action_data %>% 
  filter(grepl("S",small_area))

EN_climate_action_data <- climate_action_data %>% 
  filter(grepl("E",small_area))

str(SC_climate_action_data)

geo_lookups <- read_excel('lookups.xlsx')

SIMD2020 <- read_excel('SIMD Scotland 2020.xlsm') %>% 
  mutate(small_area=DZ11CD) %>% 
  select(-DZ11CD)

#English IMD
English_IMD2025 <- read_excel('IMD England 2025.xlsx') %>% 
  mutate(small_area=`LSOA Code`) %>% 
  select(-`LSOA Code`)

names(English_IMD2025)


sc_join <- SC_climate_action_data %>% 
  merge(SIMD2020, by = "small_area",all.x=T) %>% 
  merge(geo_lookups,by="small_area",all.x=T) %>% 
  mutate(
    simd_quintile = ntile(IMD20, 5),
    simd_decile   = ntile(IMD20, 10)
  )

sc_join %>% filter(sum<0) %>% 
  summarise(num_dzs=n())
#102 lose out

sc_join %>% 
  summarise(num_dzs=n())
#6976

102/6976

#1.5% of neighborhoods (datazones) 

write.csv(sc_join,'sc_join.csv')

en_join <- EN_climate_action_data %>% 
  merge(English_IMD2025, by = "small_area",all.x=T) %>% 
  merge(geo_lookups,by="small_area",all.x=T) %>% 
  mutate(
    imd_quintile = ntile(`LSOA IMD Ranking`, 5)
  )

names(English_IMD2025)

sc_cor_df <- sc_join %>%
  select(IMD20, sum) %>%
  correlate(method = "spearman")

sc_cor_df

ggplot(sc_join, aes(IMD20, sum)) +
  geom_point(alpha = 0.3) +
  geom_smooth(method = "loess", color = "red") +
  labs(
    x = "SIMD Rank (1 = most deprived)",
    y = "Total Co-benefit",
    title = "Relationship Between Deprivation and Total Co-benefits"
  )



#now try it with SIMD deciles
sc_cor_df_decile <- sc_join %>%
  select(simd_decile,  sum) %>%
  correlate(method = "spearman")

sc_cor_df_decile

ggplot(sc_join, aes(simd_decile, sum)) +
  geom_point(alpha = 0.3) +
  geom_smooth(method = "loess", color = "red") +
  labs(
    x = "SIMD Decile (1 = most deprived)",
    y = "Total Co-benefit",
    title = "Relationship Between Deprivation and Total Co-benefits"
  )



#England
en_cor_df <- en_join %>%
  select(`LSOA IMD Ranking`, sum) %>%
  correlate(method = "spearman")

#it's not overall social justice, richer communities benefit more, lame!
en_cor_df

ggplot(en_join, aes(`LSOA IMD Ranking`, sum)) +
  geom_point(alpha = 0.3) +
  geom_smooth(method = "loess", color = "red") +
  labs(
    x = "IMD Rank (1 = most deprived)",
    y = "Total Co-benefit",
    title = "Relationship Between Deprivation and Total Co-benefits"
  )



#let's try this and see how it plays out for diff co-benefits
benefit_cols <- c("air_quality","congestion","dampness","diet_change",
                  "excess_cold","excess_heat","hassle_costs","noise",
                  "physical_activity","road_repairs","road_safety")

en_cor_benefits <- en_join %>%
  select(`LSOA IMD Ranking`, all_of(benefit_cols)) %>%
  correlate(method = "spearman")

en_cor_benefits




sc_cor_benefits <- sc_join %>%
  select(IMD20, all_of(benefit_cols)) %>%
  correlate(method = "spearman")

sc_cor_benefits

sc_heat_df <- sc_cor_benefits %>% 
  filter(term == "IMD20") %>% 
  select(-term) %>% 
  pivot_longer(cols = everything(), names_to = "benefit", values_to = "correlation") %>% 
  mutate(benefit = reorder(benefit, correlation))


ggplot(sc_heat_df, aes(x = "IMD20", y = benefit, fill = correlation)) +
  geom_tile(color = "white") +
  scale_fill_gradient2(
    low = "#2166ac",   # blue = benefits deprived areas
    mid = "white",
    high = "#b2182b",  # red = benefits affluent areas
    midpoint = 0,
    name = "Spearman\nCorrelation"
  ) +
  labs(
    x = "Deprivation (SIMD Rank)",
    y = "Co-benefit",
    title = "Which Climate Co-benefits Flow to More vs Less Deprived Scottish Communities?"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    axis.text.x = element_blank(),
    axis.title.x = element_blank(),
    panel.grid = element_blank()
  )


sc_join %>%
  group_by(simd_decile) %>%
  summarise(mean_value = mean(air_quality, na.rm = TRUE))


benefit_cols_sum <- c("air_quality","congestion","dampness","diet_change",
                  "excess_cold","excess_heat","hassle_costs","noise",
                  "physical_activity","road_repairs","road_safety","sum")

sc_means <-  sc_join %>% 
  group_by(simd_decile) %>% 
  summarise(across(all_of(benefit_cols_sum), ~ mean(.x, na.rm = TRUE)))

#potentially negative value columns

#excess heat - 

#congestion - Negative values represent increased travel time due to factors like greater road usage via rebound effects.

#Road safety - Negative values represent decreases in road safety due to factors like increased road usage via rebound effects.

#road repair - Negative values represent increased need for repairs due to factors like greater road usage via rebound effects.

#hassle - Negative values represent increased travel time due to factors like greater road usage via rebound effects.